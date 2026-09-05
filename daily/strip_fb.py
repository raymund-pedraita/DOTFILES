import argparse
import sys
from urllib.parse import parse_qsl, unquote, urlencode, urlparse, urlunparse

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
    """Extracts the destination URL from a Facebook link wrapper, removes tracking parameters,

    and detects encrypted redirect payloads.
    """
    if not url or not isinstance(url, str):
        return ""

    raw_input = url.strip()

    # Normalize URLs missing an explicit scheme
    if not raw_input.startswith(("http://", "https://")):
        raw_input = "https://" + raw_input

    parsed = urlparse(raw_input)

    # Step 1: Unwrap Facebook shim link (e.g., l.facebook.com/l.php?u=...)
    if "facebook.com" in parsed.netloc.lower() and parsed.path.endswith("/l.php"):
        query_dict = dict(parse_qsl(parsed.query))
        if "u" in query_dict:
            target_url = unquote(query_dict["u"]).strip()

            # Catch encrypted Facebook tokens (e.g., u=AUBCkou...)
            if not target_url.startswith(("http://", "https://")):
                import urllib.request

                try:
                    req = urllib.request.Request(
                        raw_input, headers={"User-Agent": "Mozilla/5.0"}
                    )
                    with urllib.request.urlopen(req, timeout=10) as response:
                        resolved_url = response.url
                    if resolved_url == raw_input:
                        raise ValueError("Resolution did not yield a new URL")
                    return clean_facebook_url(resolved_url)
                except Exception as e:
                    raise ValueError(
                        f"Encrypted Facebook redirect token detected, and server-side resolution failed: {e}"
                    )

            parsed = urlparse(target_url)

    # Step 2: Protocol Safety Check
    if parsed.scheme.lower() not in SAFE_SCHEMES:
        raise ValueError(f"Unsafe or invalid URL protocol detected: '{parsed.scheme}'")

    # Step 3: Parse query parameters and filter out tracking keys
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

    # Step 4: Reconstruct clean URL
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Clean Facebook shim links and remove tracking parameters."
    )
    parser.add_argument("url", nargs="?", help="The Facebook wrapper URL to clean.")
    args = parser.parse_args()

    if not args.url:
        print("Error: Please provide a URL as an argument.", file=sys.stderr)
        sys.exit(1)

    try:
        cleaned = clean_facebook_url(args.url)
        print("Cleaned URL:")
        print(cleaned)
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)
