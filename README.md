# Usage

## Requirements

    mkdir -p data/
    mkdir -p data/domain/

## 1. get root tlds

    uv run get_root_tlds --data-path data

## 2. get details

    uv run get_root_tld_details --data-path data

## 3. simplify

    uv run get_root_tld_details_simplification --data-path data

# TODO
- move the data in another repository or in a branch


# Changelog
## 2025-06-25
- fix: simplification, ignore fax
- feat: simplification, + registration url if present
