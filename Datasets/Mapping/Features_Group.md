1. URL Length & Structure

| **Standard Name**          | **Meaning / Unit**                | Dataset A           | Dataset B         | Dataset C         |
| -------------------------- | --------------------------------- | ------------------- | ----------------- | ----------------- |
| `url_length`               | Total characters in URL           | `UrlLength`         | `length_url`      | `url_length`      |
| `hostname_length`          | Length of the domain/hostname     | `HostnameLength`    | `length_hostname` | `domain_length`   |
| `path_length`              | Length of path segment            | `PathLength`        | —                 | `path_length`     |
| `query_length`             | Length of query segment           | `QueryLength`       | —                 | `query_length`    |
| `subdomain_depth`          | Number of subdomain levels        | `SubdomainLevel`    | `nb_subdomains`   | `subdomain_depth` |
| `path_depth`               | Number of nested path directories | `PathLevel`         | —                 | `path_depth`      |
| `has_double_slash_in_path` | Presence of `//` beyond scheme    | `DoubleSlashInPath` | `nb_dslash`       | —                 |

2. URL Components (Special Characters)

| **Standard Name**   | **Meaning / Unit**         | Dataset A                      | Dataset B          | Dataset C                            |
| ------------------- | -------------------------- | ------------------------------ | ------------------ | ------------------------------------ |
| `num_dots`          | Count of `.`               | `NumDots`                      | `nb_dots`          | `num_dots`                           |
| `num_hyphens`       | Count of `-`               | `NumDash`, `NumDashInHostname` | `nb_hyphens`       | `num_hyphens`, `domain_hyphen_count` |
| `num_at_symbols`    | Count of `@`               | `AtSymbol`                     | `nb_at`            | `num_at`                             |
| `num_tildes`        | Count of `~`               | `TildeSymbol`                  | `nb_tilde`         | —                                    |
| `num_underscores`   | Count of `_`               | `NumUnderscore`                | `nb_underscore`    | —                                    |
| `num_percents`      | Count of `%`               | `NumPercent`                   | `nb_percent`       | `num_pct`                            |
| `num_ampersands`    | Count of `&`               | `NumAmpersand`                 | `nb_and`           | —                                    |
| `num_hashes`        | Count of `#`               | `NumHash`                      | —                  | `fragment_length` (approx.)          |
| `num_query_params`  | Number of query components | `NumQueryComponents`           | `nb_qm`, `nb_eq`   | `query_param_count`                  |
| `num_numeric_chars` | Count of digits in URL     | `NumNumericChars`              | `ratio_digits_url` | `num_digits`                         |
| `num_slashes`       | Count of `/`               | —                              | `nb_slash`         | —                                    |


3. HTTPS / Security Indicators

| **Standard Name**      | **Meaning / Unit**          | Dataset A            | Dataset B      | Dataset C              |
| ---------------------- | --------------------------- | -------------------- | -------------- | ---------------------- |
| `uses_https`           | Boolean: URL uses HTTPS     | `NoHttps` (invert)   | —              | `uses_https`           |
| `https_in_hostname`    | Hostname contains “https”   | `HttpsInHostname`    | `https_token`  | —                      |
| `http_in_path`         | Path contains “http”        | —                    | `http_in_path` | —                      |
| `has_insecure_forms`   | Form action not using HTTPS | `InsecureForms`      | `sfh`          | `form_action_external` |
| `has_submit_email`     | Form submits to email       | `SubmitInfoToEmail`  | `submit_email` | —                      |
| `has_iframe`           | iFrame tags present         | `IframeOrFrame`      | `iframe`       | `n_iframes`            |
| `has_popup`            | Popup window or JS alert    | `PopUpWindow`        | `popup_window` | —                      |
| `abnormal_form_action` | Unusual form submission     | `AbnormalFormAction` | `sfh`          | `form_action_external` |


4. Domain & Brand Features

| **Standard Name**          | **Meaning / Unit**                | Dataset A                    | Dataset B            | Dataset C                      |
| -------------------------- | --------------------------------- | ---------------------------- | -------------------- | ------------------------------ |
| `has_ip_address`           | URL contains IP instead of domain | `IpAddress`                  | `ip`                 | `domain_has_ip`, `has_ip_host` |
| `domain_in_subdomain`      | Main domain appears in subdomain  | `DomainInSubdomains`         | `tld_in_subdomain`   | —                              |
| `domain_in_path`           | Main domain appears in path       | `DomainInPaths`              | `tld_in_path`        | —                              |
| `has_random_domain`        | Random string or tokenized domain | `RandomString`               | `random_domain`      | —                              |
| `has_prefix_suffix`        | Domain has prefix/suffix (-)      | —                            | `prefix_suffix`      | —                              |
| `brand_in_subdomain`       | Brand name in subdomain           | `EmbeddedBrandName`          | `brand_in_subdomain` | —                              |
| `brand_in_path`            | Brand name in path                | `EmbeddedBrandName`          | `brand_in_path`      | —                              |
| `domain_in_brand`          | Domain and brand overlap          | —                            | `domain_in_brand`    | —                              |
| `frequent_domain_mismatch` | Domain differs from visible brand | `FrequentDomainNameMismatch` | `abnormal_subdomain` | —                              |


5. HTML / Content / Tag Features
| **Standard Name**          | **Meaning / Unit**                    | Dataset A                         | Dataset B              | Dataset C                                  |
| -------------------------- | ------------------------------------- | --------------------------------- | ---------------------- | ------------------------------------------ |
| `missing_title`            | Page has no `<title>`                 | `MissingTitle`                    | `empty_title`          | `title_len`                                |
| `external_favicon`         | Favicon hosted off-site               | `ExtFavicon`                      | `external_favicon`     | `has_favicon_external`                     |
| `external_script_ratio`    | Ratio of external JS/CSS              | `ExtMetaScriptLinkRT`             | `links_in_tags`        | `n_external_scripts`, `css_external_ratio` |
| `external_link_ratio`      | Ratio of external hyperlinks          | `PctExtHyperlinks`                | `ratio_extHyperlinks`  | `ratio_external_links`                     |
| `external_resource_ratio`  | Ratio of external resources (img/css) | `PctExtResourceUrls`              | `ratio_extMedia`       | `css_external_ratio`, `n_external_images`  |
| `null_self_redirect_ratio` | Ratio of null/self redirects          | `PctNullSelfRedirectHyperlinksRT` | `ratio_nullHyperlinks` | —                                          |
| `has_only_images_in_form`  | Forms with images only                | `ImagesOnlyInForm`                | —                      | `n_images`, `n_pw_inputs`                  |


6. Behavioral / Interaction Indicators

| **Standard Name**      | **Meaning / Unit**      | Dataset A             | Dataset B      | Dataset C            |
| ---------------------- | ----------------------- | --------------------- | -------------- | -------------------- |
| `fake_link_statusbar`  | Fake status bar message | `FakeLinkInStatusBar` | `onmouseover`  | `inline_event_attrs` |
| `right_click_disabled` | Right click blocked     | `RightClickDisabled`  | `right_clic`   | —                    |
| `popup_window`         | Popup present           | `PopUpWindow`         | `popup_window` | —                    |


7. Quantitative / Statistical Ratios

| **Standard Name**      | **Meaning / Unit**           | Dataset A              | Dataset B             | Dataset C              |
| ---------------------- | ---------------------------- | ---------------------- | --------------------- | ---------------------- |
| `ratio_ext_hyperlinks` | External links / total links | `PctExtHyperlinks`     | `ratio_extHyperlinks` | `ratio_external_links` |
| `ratio_ext_media`      | External media / total media | `PctExtResourceUrls`   | `ratio_extMedia`      | `css_external_ratio`   |
| `url_entropy`          | Shannon entropy of URL chars | `RandomString` (proxy) | —                     | `url_entropy`          |
| `char_repeat_ratio`    | Character repetition rate    | —                      | `char_repeat`         | —                      |


8. Whois / Domain Age / Popularity

| **Standard Name**            | **Meaning / Unit**           | Dataset A | Dataset B                    | Dataset C |
| ---------------------------- | ---------------------------- | --------- | ---------------------------- | --------- |
| `dns_record_exists`          | Valid DNS record found       | —         | `dns_record`                 | —         |
| `domain_registration_length` | Registration duration (days) | —         | `domain_registration_length` | —         |
| `domain_age`                 | Age in days or months        | —         | `domain_age`                 | —         |
| `web_traffic_rank`           | Alexa/SimilarWeb rank        | —         | `web_traffic`                | —         |
| `page_rank`                  | Google-style PageRank score  | —         | `page_rank`                  | —         |



9. Analysis
Dataset A focuses mostly on URL syntax & form behaviors (phishing heuristics).

Dataset B mixes lexical, structural, and domain-level features with HTML/script ratios.

Dataset C includes deep content-level metrics (scripts, forms, OpenGraph, images, entropy).

About 65% of A’s features have conceptual equivalents in B or C.