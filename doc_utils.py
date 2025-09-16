from imports import *

# Google Doc ID
DOC_ID = "1qekfk7i9iYq1M8wdb-I76zdVfyihaZHwUGfFRt1btbE"
URL = f"https://docs.google.com/document/d/{DOC_ID}/export?format=txt"

def fetch_doc_data():
    try:
        response = requests.get(URL)
        if response.status_code == 200:
            response.encoding = "utf-8"
            text = response.text

            # Signed_data
            signed_match = re.search(r'Signed_data\s*=\s*["“](.+?)["”]', text, re.DOTALL)
            signed_value = signed_match.group(1).strip() if signed_match else None

            # Approval
            approval_match = re.search(r'Approval\s*=\s*["“](.+?)["”]', text, re.DOTALL)
            approval_value = approval_match.group(1).strip() if approval_match else None

            # Approval_setting
            approval_setting_match = re.search(
                r'Approval_setting\s*=\s*["“”]?(.*?)["“”]?(?:\n|$)',
                text,
                re.IGNORECASE
            )
            approval_setting_value = approval_setting_match.group(1).strip().lower() if approval_setting_match else None
            
            # Status
            status_match = re.search(r'Status\s*=\s*["“](.+?)["”]', text, re.DOTALL)
            status_value = status_match.group(1).strip() if status_match else None

            # Version
            version_match = re.search(r'version\s*=\s*["“](.+?)["”]', text, re.DOTALL)
            version_value = version_match.group(1).strip() if version_match else None

            # URL
            url_match = re.search(r'url\s*=\s*["“](.+?)["”]', text, re.DOTALL)
            url_value = url_match.group(1).strip() if url_match else None

            # Domains
            domains_match = re.search(r'domains\s*=\s*["“](.+?)["”]', text, re.DOTALL)
            domains_value = domains_match.group(1).strip() if domains_match else None
            domain_list = [d.strip().lower() for d in domains_value.split(",")] if domains_value else []

            # ✅ Return as dictionary
            return {
                "signed_value": signed_value,
                "approval_value": approval_value,
                "approval_setting": approval_setting_value,
                "status": status_value,
                "version": version_value,
                "url": url_value,
                "domains": domain_list
            }
        else:
            return {}
    except Exception:
        return {}
