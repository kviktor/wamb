import time

import httpx2

from app.metadata.models import ResponseLog


class Client:
    def get_headers(self):
        return {"User-Agent": "wamb - where are my books?"}

    def get_sleep(self, retry_count: int) -> float:
        return retry_count * 1.0

    def log_response(self, response, exc):
        if response:
            content_type = response.headers.get("Content-Type", "")
            if content_type in ("text/html", "application/json"):
                response_content = response.text
            elif content_type.startswith("image/"):
                response_content = "/* raw image */"
            else:
                response_content = str(response.content)

            status_code = response.status_code
            url = str(response.url)
            method = response._request.method
        else:
            status_code = 0
            response_content = ""
            url = exc._request.url
            method = exc._request.method

        ResponseLog.objects.create(
            service=self.SERVICE,
            url=url,
            method=method,
            response=response_content,
            status_code=status_code,
            exc=str(exc),
        )

    def get(self, url, **kwargs):
        return self.request("get", url, **kwargs)

    def head(self, url, **kwargs):
        return self.request("head", url, **kwargs)

    def request(self, method, url, retries=0, **kwargs) -> httpx2.Response | None:
        if retries > 3:
            return None

        if retries > 0:
            time.sleep(self.get_sleep(retries))

        try:
            fnc = getattr(httpx2, method)
            response = fnc(
                url, headers=self.get_headers(), follow_redirects=True, **kwargs
            )
            response.raise_for_status()
            self.log_response(response, None)
            return response
        except (httpx2.RequestError, httpx2.StreamError) as exc:
            self.log_response(None, exc)
            return self.request(method, url, retries=retries + 1, **kwargs)
        except httpx2.HTTPStatusError as exc:
            self.log_response(response, exc)
            if exc.response.status_code >= 500:
                return self.request(method, url, retries=retries + 1, **kwargs)

        return None
