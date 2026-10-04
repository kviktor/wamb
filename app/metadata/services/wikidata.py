from datetime import datetime
from urllib.parse import quote
import hashlib
import logging

from app.metadata.models import Service
from app.metadata.services.client import Client

logger = logging.getLogger(__name__)


def get_claim_values(data, claim):
    claims = []
    for item in data.get("claims", {}).get(claim, []):
        mainsnak = item.get("mainsnak")
        if not mainsnak:
            continue

        datavalue = mainsnak.get("datavalue")
        if not datavalue:
            continue

        if datavalue["type"] in ("wikibase-item", "wikibase-entityid"):
            value_id = datavalue.get("value", {}).get("id")
            if value_id:
                claims.append(value_id)
        else:
            value = datavalue.get("value")
            claims.append(value)

    return claims


def get_image_url(data) -> str | None:
    names = get_claim_values(data, "P18")
    for name in names:
        name = name.replace(" ", "_")

        name_hash = hashlib.md5(name.encode()).hexdigest()
        quoted_name = quote(name)
        return (
            f"https://upload.wikimedia.org/wikipedia/commons/thumb/"
            f"{name_hash[:1]}/{name_hash[:2]}/"
            f"{quoted_name}/500px-{quoted_name}"
        )


class WikidataClient(Client):
    BASE_URL = "https://www.wikidata.org"
    SERVICE = Service.wikidata

    def search(self, name: str) -> str | None:
        response = self.get(
            f"{self.BASE_URL}/w/api.php",
            params={
                "action": "wbsearchentities",
                "search": name,
                "language": "en",
                "format": "json",
            },
        )

        try:
            results = response.json().get("search", [])
            for result in results:
                data = self.get_entity_data(result["id"])

                # we only look for humans
                if "Q5" in get_claim_values(data, "P31"):
                    return data

        except IndexError, KeyError, Exception:
            logger.warning("wikidata search failure", exc_info=True)
            return None

    def get_entity_data(self, wiki_id: str) -> str | None:
        response = self.get(f"{self.BASE_URL}/wiki/Special:EntityData/{wiki_id}.json")

        try:
            return response.json().get("entities", {}).get(wiki_id)
        except IndexError, KeyError, Exception:
            logger.warning("wikidata get_entity_data failure", exc_info=True)
            return None


def resolve_item_id(qid: str, claim: str) -> str | None:
    from app.metadata.models import WikidataCache

    try:
        return WikidataCache.objects.get(qid=qid, claim=claim).value
    except WikidataCache.DoesNotExist:
        data = WikidataClient().get_entity_data(qid)
        if value := get_claim_values(data, claim):
            WikidataCache.objects.create(
                qid=qid,
                claim=claim,
                value=value[0],
            )

            return value[0]

        return None


def update_author(author) -> None:
    client = WikidataClient()
    data = client.search(author.name)
    if not data:
        return

    values = {
        "country": "",
        "gender": "",
        "birth_date": None,
        "image": None,
    }

    gender = get_claim_values(data, "P21")
    if gender:
        values["gender"] = resolve_item_id(gender[0], "P2572")

    country = get_claim_values(data, "P27")
    if country:
        values["country"] = resolve_item_id(country[0], "P297")

    isni = get_claim_values(data, "P213")
    if isni:
        isni = isni[0]

    birth_date = get_claim_values(data, "P569")
    if birth_date:
        birth_date = birth_date[0]["time"].lstrip("+").replace("Z", "+00:00")
        if "-00" in birth_date:
            birth_date = birth_date.replace("-00", "-01")

        try:
            values["birth_date"] = datetime.fromisoformat(birth_date)
        except Exception:
            logger.exception("wikidata.invalid_birth_date")

    image = get_image_url(data)
    if image and not author.image_id:
        from app.books.utils import get_or_create_image

        values["image"] = get_or_create_image(image)

    update_fields = []
    if isni and author.third_party_data.get("isni") != isni:
        author.third_party_data["isni"] = isni
        update_fields.append("third_party_data")

    for field_name, value in values.items():
        if value and getattr(author, field_name) != value:
            setattr(author, field_name, value)
            update_fields.append(field_name)

    if update_fields:
        author.save(update_fields=update_fields)
