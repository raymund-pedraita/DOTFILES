from urllib.parse import parse_qsl, unquote, urlencode, urlparse, urlunparse
import urllib.request

FB_TRACKING_PARAMS = {
    "fbclid",
    "h",
    "__tn__",
    "fb_action_ids",
    "fb_action_types",
    "fb_source",
    "fb_ref",
    "ref",
}

SAFE_SCHEMES = {"http", "https"}

def clean_facebook_url(url: str) -> str:
    if not url or not isinstance(url, str):
        return ""

    raw_input = url.strip()

    if not raw_input.startswith(("http://", "https://")):
        raw_input = "https://" + raw_input

    parsed = urlparse(raw_input)

    if "facebook.com" in parsed.netloc.lower() and parsed.path.endswith("/l.php"):
        query_dict = dict(parse_qsl(parsed.query))
        if "u" in query_dict:
            target_url = unquote(query_dict["u"]).strip()

            if not target_url.startswith(("http://", "https://")):
                # Resolve via HTTP request
                try:
                    req = urllib.request.Request(
                        raw_input, headers={"User-Agent": "Mozilla/5.0"}
                    )
                    with urllib.request.urlopen(req) as response:
                        resolved_url = response.url
                    # If it's still the same URL (no redirect), fail
                    if resolved_url == raw_input:
                        raise ValueError("Resolution did not yield a new URL")
                    return clean_facebook_url(resolved_url)
                except Exception as e:
                    raise ValueError(
                        f"Encrypted Facebook redirect token detected, and server-side resolution failed: {e}"
                    )

            parsed = urlparse(target_url)

    if parsed.scheme.lower() not in SAFE_SCHEMES:
        raise ValueError(f"Unsafe or invalid URL protocol detected: '{parsed.scheme}'")

    query_params = parse_qsl(parsed.query, keep_blank_values=False)
    cleaned_params = []

    for key, value in query_params:
        key_lower = key.lower()

        is_tracking_param = (
            key_lower in FB_TRACKING_PARAMS
            or key_lower.startswith("c[")
            or key_lower.startswith("_aem")
            or key_lower.startswith("aem_")
            or key_lower.startswith("__cft")
        )

        if not is_tracking_param:
            cleaned_params.append((key, value))

    clean_query = urlencode(cleaned_params) if cleaned_params else ""

    return urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            clean_query,
            parsed.fragment,
        )
    )

print(clean_facebook_url('https://l.facebook.com/l.php?u=AUBCkou0cVr6nCCxybNXuN2Xg5AMqmSw2fVVlR8C1WJdGp8BjwYkwEPnn73ZeQroR9I_dhCUoGGFfGNxE7sIaOJoBes6dQbF6fErvnzfBVyU5KIcSRI7bXLAy5hHChll5ApAt2YMUhnYV9raj56bEtiw_jAtkLMFQCm27czYzjGyR2B034RtE1xMHRse5yVk4-quWRpOdRuPmNzpIsFhvqktsQRHi-KFx_8S334aacll0yy-SLu1NJ9ro0RlGiY-Cx-BKn9L0oX0MPO2JCqvD3KRRTWAfeA06e-MnmFlRqKo6veaz2KYVDkNZFAO7UB3zLG1Zg6jD0AlO_HTLoVztKBqCcYQcv4ZR2bFd3t2eJ0AmyG08iATfLH1mOBMHB0RlvPggdSnVJy54npJx9jwOTbKGeAx4eVwwvIJNVn6w6DRTagAsXB2GkzMXELxXew8-iAkGQNRcuADKnOOF_B8Uu2re5H0-lUk3WRZXL4NaaPS0sI_1zm06rtkgtOTn_-V3FloXVsc1nNQx53hL7hcAgHM4XlP9iFoGg&h=AUBvSafJn2OKbwLrrL4-9utW3kgaRmWxhxowkuna1GzNcAy0FYsT5iH9TWVhoUFDr2eGcOI1N8tyhi6n3Y0ZcC0X4886aXiXWnXyujqwgaNKb6hBbSOCAEDV-T_ZuwqkyicpUMeIWNkk_QVFdgubsjAK02oK&__cft__[0]=AZgmpxkq9YkM9NT42zpwCKM-UgVZ7L1jKWY5V1aY8NdDHOs7A_C4coUlqOJ9u0wVGGkH5Dx9dwP3s2HF-SHzGdEzT7J0jV4uxlCiyS8qc6QtQ_0xvacNY7gAY7p4Zi-f3cUbDVSKdfFGfawno04WhuqtlUTwtt_idPd0IHxQvHSR3GQjku6fxvyIyXY1sQqeFcuRJCgLmLd9tScW3TX_7TfQTxdb1zQnLqE0xm1NMR1us8dBMoIoZUBoDlCblUWmXY0cedEkNUamxa0Zw3bsFCrejcForFBEg73VVswCAB3gb7MqXMkP_nvM&__tn__=%2CmH-R'))
