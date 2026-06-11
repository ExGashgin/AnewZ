import re
import pandas as pd
import streamlit as st

# Set up clean app styling
st.set_page_config(page_title="AnewZ Link Tracker", page_icon="🔗", layout="centered")

st.title("🔗 AnewZ TV Bulk Link Tracker")
st.write("Paste your raw article URLs below to instantly convert them into GA4-tracked URLs for your broadcast graphics team.")

# Input box for multiple URLs
urls_input = st.text_area(
    "Enter Article URLs (One per line):",
    height=200,
    placeholder="https://anewz.tv/region/middle-east/20751/iran-hits-back-at-us-bases-after-american-overnight-strikes/news"
)

if st.button("Convert Links", type="primary"):
    if not urls_input.strip():
        st.error("Please paste at least one URL.")
    else:
        urls = [url.strip() for url in urls_input.split("\n") if url.strip()]
        
        tracked_links_list = []
        data_for_csv = []
        
        for url in urls:
            try:
                # Automatically extract the article slug/headline for the GA4 campaign name
                match = re.search(r"/([^/]+)/news", url)
                campaign_name = match.group(1) if match else "tv_broadcast"
                
                # Stitch together the automated tracking link
                tracked_url = f"{url}?utm_source=tv&utm_medium=qr_code&utm_campaign={campaign_name}"
                
                tracked_links_list.append(tracked_url)
                data_for_csv.append({"Original URL": url, "Tracked URL": tracked_url, "Campaign Name": campaign_name})
                
            except Exception as e:
                st.warning(f"Skipped invalid URL layout: {url}")

        if tracked_links_list:
            st.success(f"Successfully converted {len(tracked_links_list)} links!")
            
            # Display the tracked links in a clean text area so they can be copied instantly
            output_text = "\n".join(tracked_links_list)
            st.text_area("Your Tracked URLs (Copy & Paste):", value=output_text, height=250)
            
            # Turn data into a DataFrame for a nice preview and download capability
            df = pd.DataFrame(data_for_csv)
            
            # Convert DataFrame to CSV format for download
            csv_data = df.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 Download List as CSV (Excel)",
                data=csv_data,
                file_name="anewz_tracked_links.csv",
                mime="text/csv",
                use_container_width=True
            )
