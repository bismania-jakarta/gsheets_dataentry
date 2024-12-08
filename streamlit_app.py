import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd 
import gspread

# 1st line on secret.toml -> spreadsheets="https://docs.google.com/spreadsheets/d/1RBzRj4gjC62bS_FlDlbeMpFiieq3QPFY5N3udv4zF0M"

# Display title and description
st.title('Vendor Management Portal')
st.markdown('Enter the details of the new vendor below.')

#using this coding github: https://github.com/streamlit/gsheets-connection
url = "https://docs.google.com/spreadsheets/d/1RBzRj4gjC62bS_FlDlbeMpFiieq3QPFY5N3udv4zF0M"

bs_tmycalc = "https://docs.google.com/spreadsheets/d/1qzOFK8M3sxOogESmajWn-kspoGJBkrwmI6oB0A5DkVg"

# Establishing a google sheets connections
#conn = st.experimental_connection("gsheets", type=GSheetsConnection)
bsconnect = st.connection("gsheets", type=GSheetsConnection)

# Fetch existing vendors data, to return to pandas dataframe
#df_existing_data = bsconnect.read(worksheets='Vendors', usecols=list(range(6)), ttl=5) # catched to 5 secs
#-> form that github: df_existing_data = connn.read(spreadsheet=url, usecols=[0, 1])
df_existing_data = bsconnect.read(spreadsheet=url)

# it works -> df_bs_tmycalc = bsconnect.read(spreadsheet=bs_tmycalc)

# To make sure we dont have empty rows
df_existing_data = df_existing_data.dropna(how='all')

# 2baris di bawah ini juga gak berhasil
#url = "https://docs.google.com/spreadsheets/d/1RBzRj4gjC62bS_FlDlbeMpFiieq3QPFY5N3udv4zF0M"
#df_existing_data = pd.read_html(url, header=0)[0]

# baca function di bawah ini juga gak berhasil
#def convert_google_sheet_url(url):
    # Regular expression to match and capture the necessary part of the URL
#    pattern = r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)(/edit#gid=(\d+)|/edit.*)?'

    # Replace function to construct the new URL for CSV export
    # If gid is present in the URL, it includes it in the export URL, otherwise, it's omitted
#    replacement = lambda m: f'https://docs.google.com/spreadsheets/d/{m.group(1)}/export?' + (f'gid={m.group(3)}&' if m.group(3) else '') + 'format=csv'

    # Replace using regex
#    new_url = re.sub(pattern, replacement, url)
#    return new_url

#url = "https://docs.google.com/spreadsheets/d/1RBzRj4gjC62bS_FlDlbeMpFiieq3QPFY5N3udv4zF0M"
#new_url = convert_google_sheet_url(url)
#st.write(new_url)
#df_existing_data = pd.read_csv(new_url)

# 2baris di bawah ini juga error
#file_name = "https://github.com/bosimanurung/wespilift2/blob/main/tmycalc.csv"
#df_existing_data = pd.read_csv(file_name)

st.dataframe(df_existing_data, hide_index=True)

#st.write('')
# it works -> st.dataframe(df_bs_tmycalc, hide_index=True)

# List of Business type and products
business_types = ['Manucfacturer', 'Distributor', 'Wholesaler', 'Retailer', 'Service Provider']
products = ['Electronics', 'Apparel', 'Groceries', 'Software', 'Other']

# Onboarding new vendor form
with st.form(key='vendor_form'):
    company_name = st.text_input(label='Company Name*')
    typeOfBusiness = st.selectbox('Type of business*', options=business_types, index=None)
    products = st.multiselect('Products Offered', options=products)
    years_in_business = st.slider('Years in business', 0, 50, 5)
    onboarding_date = st.date_input(label='Orboarding Date')
    additional_info = st.text_area(label='Additional Notes')

    # mark mandatory field
    st.markdown('**required*')

    submit_button = st.form_submit_button(label='Submit Vendor Details')

    # if submit button is pressed
    if submit_button:
        #st.write('You pressed submit')
        # check if all mandatory fields are filled
        if not company_name or not typeOfBusiness:
            st.warning('Ensure all mandatory fields are filled.')
            st.stop()
        elif df_existing_data["CompanyName"].str.contains(company_name).any():
            st.warning("A vendor with this company name already exist.")
            st.stop()
        else:
            # Create a new row of vendor data
            vendor_data = pd.DataFrame(
                [
                    {
                        "CompanyName": company_name, 
                        "BusinessType": typeOfBusiness, 
                        "Products": ", ".join(products),
                        "YearsInBusiness": years_in_business,
                        "OnBoardingDate": onboarding_date.strftime("%Y-%m-%d"),
                        "AdditionalInfo": additional_info                     
                    }
                ]
            )
        
        # add the new vendor data to the existing data
        updated_df = pd.concat([df_existing_data, vendor_data], ignore_index=True)

        # update google sheets with new vendor data
        bsconnect.update(spreadsheet=url, worksheet="Vendors", data=updated_df)

        st.success('Vendor details successfully submitted!')
