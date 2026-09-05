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
    """Extracts the true destination URL from a Facebook link shim wrapper,

    strips out tracking parameters, and ensures the target scheme is safe.
    """
    if not url or not isinstance(url, str):
        return ""

    parsed = urlparse(url.strip())

    # Step 1: Unwrap Facebook shim link (e.g., l.facebook.com/l.php?u=...)
    if "facebook.com" in parsed.netloc.lower() and parsed.path.endswith("/l.php"):
        query_dict = dict(parse_qsl(parsed.query))
        if "u" in query_dict:
            target_url = unquote(query_dict["u"])
            parsed = urlparse(target_url)

    # Step 2: Safety Check - Ensure URL scheme is valid and safe (HTTP/HTTPS)
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
        )

        if not is_tracking_param:
            cleaned_params.append((key, value))

    # Step 4: Reconstruct clean URL
    clean_query = urlencode(cleaned_params) if cleaned_params else ""

    cleaned_url = urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            clean_query,
            parsed.fragment,
        )
    )

    return cleaned_url


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Clean Facebook shim links and remove tracking query parameters."
    )
    parser.add_argument(
        "url",
        nargs="?",
        help="The Facebook wrapper URL to clean (optional if running default example).",
    )
    args = parser.parse_args()

    # Default fallback URL if no CLI argument is passed
    default_url = (
        "https://l.facebook.com/l.php?u=https%3A%2F%2Fthehackernews.com%2F2026%2F09%2F"
        "google-releases-chrome-update-to-patch.html%3Ffbclid%3DIwcGRvZgVleHRuA2Fl"
        "bQIxMABicmlkETFQRVY5QjZ0NWFraFEzYnpzc3J0YwZhcHBfaWQQMjIyMDM5MTc4ODIwMDg5Mg"
        "ABHuHlHG85DA1UzckatmLsHSnCYLxHLOsdkim6f2c0eINetIU4U00rFTx-_E0k_aem_zF9avh8"
        "lUdWAuaohhwH0cA&h=AUDg_vfW3EkVqSvMi3XasEUYtU1fziFwXzSntH2LtJtb7_FyMgMooI8s"
        "tonGRKweqsutDeUW81Qh1989rSOiahcu2V-OFM-iGvz82HgOnlFO1NQ1NYBVU9iU598vfBxmpm"
        "WW1JwwHTKW2phKiYuU0SEjyWGjLTyRO-hjCA&__tn__=-UK-R&c[0]=AUCpctp09Bj9aFjnqCY"
        "LWJAEGv9JqutEucwObzLh1KXFmL68wAkL7_hVIFHyvCuh0_TFDWM7auNc5h68f5by6eSzR1nyIH"
        "RDpQvgpfh8fh7AVSbUF6oqjz5oe9LM0Njtg5LEI6JYEzbvI4E4ODrUlfOGKw0k_ZFVGDOE0V60"
        "6FuN8GnkC9eh9cqjLxwkpp4bCmLW6l9YYp2FCClCnBCBwnamcTVucao"
    )

    input_url = args.url if args.url else default_url

    try:
        cleaned = clean_facebook_url(input_url)
        print("Cleaned URL:")
        print(cleaned)
    except ValueError as err:
        print(f"Security Error: {err}", file=sys.stderr)
