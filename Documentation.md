### Feature Definition
1. Lexical URL Features These features are derived strictly from the character string of the URL.  
| ID | Name | Type | Definition |
|:---:|:---:|:---:|:---:|
|1|url_lenght|int|The total number of character string of the URL|
|2|hostname_lenght|int|The number of characters in the domain name|
|3|path_lenght|int|The number of characters in the file path (the section after the TLD)|
|4|query_lenght|int|The number of characters in the query string (the section after the ?)|
|5|num_dots|int|count of . characters in the URL. Multiple dots often indicate subdomain spoofing|
|6|num_hyphens|int|count of - characters. frequently use hyphens to mimic legitimate brand names|
|7|num_at_symbols|int|The count of @ characters. Browsers ignore everything before the @ symbol, allowing attackers to trick users|
|8|path_depth|int|Counts the depth of the path in webpage URL|
|9|subdomain_depth|int|The number of dot-separated segments in the hostname, minus 2|
|10|num_percents|float|The count of the percentage symbol (%) within the full URL string|
|11|num_numeric_chars|int|The total count of numeric digits (0-9) present in the full URL|
  
2. Host-Based Features  
| ID | Name | Type | Definition |
|:---:|:---:|:---:|:---:|
|12|has_ip_address|boolean|Returns 1 if the hostname is a raw IP address (e.g., 192.168.1.1) rather than a domain name. Legitimate public sites rarely use raw IPs|
|13|uses_https|boolean|Returns 1 if the URL uses the https protocol|
  
3. Content-Based Features These features are extracted from the HTML source code or DOM tree of the webpage  
| ID | Name | Type | Definition |
|:---:|:---:|:---:|:---|
|14|missing_title|boolean|Returns 1 if the HTML `<title>` tag is empty or missing|
|15|has_iframe|boolean|Returns 1 if the page contains `<iframe>` tags, often used to overlay a fake login box on top of legitimate content|
|16|has_images|boolean|Returns 1 if the page loads any images. Some low-effort phishing pages are text-only|
|17|popup_window|boolean|Returns 1 if the page includes scripts to spawn pop-up windows|
|18|submit_email|boolean|Returns 1 if an HTML form action uses the `mailto:` protocol|
|19|abnormal_form_action|boolean|Returns 1 if a form action points to a suspicious target, such as `#`, `about:blank`, an empty string, or `javascript:true`|
|20|external_favicon|boolean|Returns 1 if the favicon (site icon) is loaded from a domain different from the URL's domain|
|21|external_css_ratio|float|The ratio of CSS stylesheets loaded from external domains to the total number of CSS files|
|22|ratio_external_links|float|The percentage of hyperlinks (`<a>` tags) that point to external domains|
|23|ratio_null_links|float|The percentage of hyperlinks that point to nowhere. High ratios indicate a hastily cloned template where functional links were broken|
