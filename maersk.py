from dataclasses import dataclass, field
from urllib.parse import urljoin, urlencode
from dotenv import load_dotenv
import zeep
from zeep.transports import Transport
import ssl
import requests
import xml.etree.ElementTree as ET

load_dotenv()


@dataclass
class MaerskApi():
	base_api_url: str = 'https://pilotws.pilotdelivers.com'
	wsdl_url: str = 'https://pilotws.pilotdelivers.com/copilotforms/wsCoPilotSG.asmx?WSDL'
	session: requests.Session = field(default_factory=requests.Session)

	def get_new_quote(self):
		settings = zeep.Settings(strict=False)

		self.session.headers.update({
			"Content-Type": "application/soap+xml; charset=utf-8"
		})

		# self.session.verify = 'certificates/server.pem'
		self.session.verify = False

		wsdl_url = "https://ws.pilotair.com/tms2.1/tms/PilotServiceRequest.asmx?WSDL"

		transport = Transport(session=self.session)
		zeep_client = zeep.Client(wsdl=wsdl_url, transport=transport, settings=settings)

		try:
			response = zeep_client.service.GetNewQuote()
			return response
		except Exception as e:
			print("Error:", e)
			return None

	def get_new_quote_rest(self):
		endpoint = 'https://ws.pilotair.com/tms2.1/tms/PilotServiceRequest.asmx/GetNewQuote'

		try:
			with requests.Session() as client:
				response = client.get(endpoint, verify=False)
			response.raise_for_status()
			return response
		except Exception as e:
			print(f"Error occurred: {e}")
			return None

	def find_origin_by_zip_rest(self, sZip):
		endpoint = urljoin(self.base_api_url, '/copilotforms/wsCoPilotSG.asmx/FindOriginByZip')

		payload = {'sZip': sZip}
		encoded_payload = urlencode(payload)
		content_length = str(len(encoded_payload))

		headers = {
			'Content-Type': 'application/x-www-form-urlencoded',
			'Content-Length': content_length
		}

		self.client.headers.update(headers)
		try:
			response = self.client.post(endpoint, data=encoded_payload)
			response.raise_for_status()
			return response
		except Exception as e:
			print(f"Error occurred: {e}")
			return None

	def find_origin_by_zip(self, sZip):
		self.session.headers.update({
			"Content-Type": "application/soap+xml; charset=utf-8",
		})

		wsdl_url = "https://pilotws.pilotdelivers.com/copilotforms/wsCoPilotSG.asmx?WSDL"

		transport = Transport(session=self.session)
		zeep_client = zeep.Client(wsdl=wsdl_url, transport=transport)

		try:
			return zeep_client.service.FindOriginByZip(sZip=sZip)
		except Exception as e:
			print("Error:", e)

	def service_info_rest(self, sOriginZip, sDestZip):
		endpoint = urljoin(self.base_api_url, '/copilotforms/wsCoPilotSG.asmx/ServiceInfo')

		payload = {
			'sOriginZip': sOriginZip,
			'sDestZip': sDestZip
		}
		encoded_payload = urlencode(payload)
		content_length = str(len(encoded_payload))

		headers = {
			'Content-Type': 'application/x-www-form-urlencoded',
			'Content-Length': content_length
		}

		self.client.headers.update(headers)
		try:
			response = self.client.post(endpoint, data=encoded_payload)
			response.raise_for_status()
			return response
		except Exception as e:
			print(f"Error occurred: {e}")
			return None

	def service_info(self, sOriginZip, sDestZip):
		self.session.headers.update({
			"Content-Type": "application/soap+xml; charset=utf-8",
		})

		wsdl_url = "https://pilotws.pilotdelivers.com/copilotforms/wsCoPilotSG.asmx?WSDL"

		transport = Transport(session=self.session)
		zeep_client = zeep.Client(wsdl=wsdl_url, transport=transport)

		try:
			return zeep_client.service.ServiceInfo(sOriginZip=sOriginZip, sDestZip=sDestZip)
		except Exception as e:
			print("Error:", e)

	def get_rating_rest(self, ratingRootObject):
		endpoint = 'https://www.pilotssl.com/pilotapi/v1/Ratings'

		payload = ratingRootObject
		# encoded_payload = urlencode(payload)
		# content_length = str(len(encoded_payload))

		headers = {
			'Content-Type': 'application/json',
			'Accept': 'text/plain',
			'api-key': '9AC336ED-722D-440E-9439-43AFEA65D884'
		}

		try:
			with requests.Session() as client:
				client.headers.update(headers)
				response = client.post(endpoint, verify=False, json=payload)
			response.raise_for_status()
			return response.json()
		except Exception as e:
			print(f"Error occurred: {e}")
			return None

	def xml_to_dict(self, xml_string):
	    # Parse the XML string
	    root = ET.fromstring(xml_string)

	    # Define the namespaces
	    namespaces = {
	        'diffgr': 'urn:schemas-microsoft-com:xml-diffgram-v1',
	        'msdata': 'urn:schemas-microsoft-com:xml-msdata',
	        '': 'http://tempuri.org/dsTQSQuote.xsd'
	    }

	    # Find the TQSQuote element
	    tqs_quote = root.find('.//diffgr:diffgram/dsTQSQuote/TQSQuote', namespaces)

	    if tqs_quote is None:
	        raise ValueError("TQSQuote element not found in the XML.")

	    # Helper function to extract text from an element
	    def get_text(element, tag):
	        if element is None:
	            return ''
	        child = element.find(tag, namespaces)
	        return child.text if child is not None else ''

	    # Construct the dictionary
	    result = {
	        "Rating": {
	            "TQSQuoteID": tqs_quote.attrib.get('diffgr:id', ''),
	            "QuoteID": get_text(tqs_quote, 'QuoteID'),
	            "TariffID": get_text(tqs_quote, 'TariffID'),
	            "Scale": get_text(tqs_quote, 'Scale'),
	            "LocationID": get_text(tqs_quote, 'LocationID'),
	            "TransportByAir": get_text(tqs_quote, 'TransportByAir'),
	            "CalculateBillCode": get_text(tqs_quote, 'CalculateBillCode'),
	            "IsSaveQuote": get_text(tqs_quote, 'IsSaveQuote'),
	            "IATA_Classifications": get_text(tqs_quote, 'IATA_Classifications'),
	            "PackingContainers": get_text(tqs_quote, 'PackingContainers'),
	            "DeclaredValue": get_text(tqs_quote, 'DeclaredValue'),
	            "InsuranceValue": get_text(tqs_quote, 'InsuranceValue'),
	            "COD": get_text(tqs_quote, 'COD'),
	            "TariffName": get_text(tqs_quote, 'TariffName'),
	            "Notes": get_text(tqs_quote, 'Notes'),
	            "Service": get_text(tqs_quote, 'Service'),
	            "QuoteDate": get_text(tqs_quote, 'QuoteDate'),
	            "ChargeWeight": get_text(tqs_quote, 'ChargeWeight'),
	            "TotalPieces": get_text(tqs_quote, 'TotalPieces'),
	            "Shipper": {
	                "Name": get_text(tqs_quote.find('Shipper', namespaces), 'Name'),
	                "PDArea": get_text(tqs_quote.find('Shipper', namespaces), 'PDArea'),
	                "Address1": get_text(tqs_quote.find('Shipper', namespaces), 'Address1'),
	                "Address2": get_text(tqs_quote.find('Shipper', namespaces), 'Address2'),
	                "City": get_text(tqs_quote.find('Shipper', namespaces), 'City'),
	                "State": get_text(tqs_quote.find('Shipper', namespaces), 'State'),
	                "Zipcode": get_text(tqs_quote.find('Shipper', namespaces), 'Zipcode'),
	                "Airport": get_text(tqs_quote.find('Shipper', namespaces), 'Airport'),
	                "Attempted": get_text(tqs_quote.find('Shipper', namespaces), 'Attempted'),
	                "PrivateRes": get_text(tqs_quote.find('Shipper', namespaces), 'PrivateRes'),
	                "Hotel": get_text(tqs_quote.find('Shipper', namespaces), 'Hotel'),
	                "Inside": get_text(tqs_quote.find('Shipper', namespaces), 'Inside'),
	                "Liftgate": get_text(tqs_quote.find('Shipper', namespaces), 'Liftgate'),
	                "TwoManHours": get_text(tqs_quote.find('Shipper', namespaces), 'TwoManHours'),
	                "WaitTimeHours": get_text(tqs_quote.find('Shipper', namespaces), 'WaitTimeHours'),
	                "Special": get_text(tqs_quote.find('Shipper', namespaces), 'Special'),
	                "DedicatedVehicle": get_text(tqs_quote.find('Shipper', namespaces), 'DedicatedVehicle'),
	                "Miles": get_text(tqs_quote.find('Shipper', namespaces), 'Miles'),
	                "Canadian": get_text(tqs_quote.find('Shipper', namespaces), 'Canadian'),
	                "ServiceCode": get_text(tqs_quote.find('Shipper', namespaces), 'ServiceCode'),
	                "Convention": get_text(tqs_quote.find('Shipper', namespaces), 'Convention'),
	                "Country": get_text(tqs_quote.find('Shipper', namespaces), 'Country'),
	                "IsBeyond": get_text(tqs_quote.find('Shipper', namespaces), 'IsBeyond'),
	                "BeyondServiceArea": get_text(tqs_quote.find('Shipper', namespaces), 'BeyondServiceArea'),
	                "Station": get_text(tqs_quote.find('Shipper', namespaces), 'Station'),
	                "AirtrakNo": get_text(tqs_quote.find('Shipper', namespaces), 'AirtrakNo')
	            },
	            "Consignee": {
	                "Name": get_text(tqs_quote.find('Consignee', namespaces), 'Name'),
	                "PDArea": get_text(tqs_quote.find('Consignee', namespaces), 'PDArea'),
	                "Address1": get_text(tqs_quote.find('Consignee', namespaces), 'Address1'),
	                "Address2": get_text(tqs_quote.find('Consignee', namespaces), 'Address2'),
	                "City": get_text(tqs_quote.find('Consignee', namespaces), 'City'),
	                "State": get_text(tqs_quote.find('Consignee', namespaces), 'State'),
	                "Zipcode": get_text(tqs_quote.find('Consignee', namespaces), 'Zipcode'),
	                "Airport": get_text(tqs_quote.find('Consignee', namespaces), 'Airport'),
	                "Attempted": get_text(tqs_quote.find('Consignee', namespaces), 'Attempted'),
	                "PrivateRes": get_text(tqs_quote.find('Consignee', namespaces), 'PrivateRes'),
	                "Hotel": get_text(tqs_quote.find('Consignee', namespaces), 'Hotel'),
	                "Inside": get_text(tqs_quote.find('Consignee', namespaces), 'Inside'),
	                "Liftgate": get_text(tqs_quote.find('Consignee', namespaces), 'Liftgate'),
	                "TwoManHours": get_text(tqs_quote.find('Consignee', namespaces), 'TwoManHours'),
	                "WaitTimeHours": get_text(tqs_quote.find('Consignee', namespaces), 'WaitTimeHours'),
	                "Special": get_text(tqs_quote.find('Consignee', namespaces), 'Special'),
	                "DedicatedVehicle": get_text(tqs_quote.find('Consignee', namespaces), 'DedicatedVehicle'),
	                "Miles": get_text(tqs_quote.find('Consignee', namespaces), 'Miles'),
	                "Canadian": get_text(tqs_quote.find('Consignee', namespaces), 'Canadian'),
	                "ServiceCode": get_text(tqs_quote.find('Consignee', namespaces), 'ServiceCode'),
	                "Convention": get_text(tqs_quote.find('Consignee', namespaces), 'Convention'),
	                "Country": get_text(tqs_quote.find('Consignee', namespaces), 'Country'),
	                "IsBeyond": get_text(tqs_quote.find('Consignee', namespaces), 'IsBeyond'),
	                "BeyondServiceArea": get_text(tqs_quote.find('Consignee', namespaces), 'BeyondServiceArea'),
	                "Station": get_text(tqs_quote.find('Consignee', namespaces), 'Station'),
	                "AirtrakNo": get_text(tqs_quote.find('Consignee', namespaces), 'AirtrakNo')
	            },
	            "LineItems": [
	                {
	                    "LineRow": get_text(line_item, 'LineRow'),
	                    "Pieces": get_text(line_item, 'Pieces'),
	                    "Weight": get_text(line_item, 'Weight'),
	                    "Description": get_text(line_item, 'Description'),
	                    "Length": get_text(line_item, 'Length'),
	                    "Width": get_text(line_item, 'Width'),
	                    "Height": get_text(line_item, 'Height')
	                }
	                for line_item in tqs_quote.findall('LineItems', namespaces)
	            ],
	            "Quote": {
	                "Service": get_text(tqs_quote.find('Quote', namespaces), 'Service'),
	                "DimWeight": get_text(tqs_quote.find('Quote', namespaces), 'DimWeight'),
	                "TotalQuote": get_text(tqs_quote.find('Quote', namespaces), 'TotalQuote'),
	                "Breakdown": {
	                    "ChargeCode": get_text(tqs_quote.find('Quote/Breakdown', namespaces), 'ChargeCode'),
	                    "Charge": get_text(tqs_quote.find('Quote/Breakdown', namespaces), 'Charge'),
	                    "BillCodeName": get_text(tqs_quote.find('Quote/Breakdown', namespaces), 'BillCodeName'),
	                    "Steps": get_text(tqs_quote.find('Quote/Breakdown', namespaces), 'Steps')
	                },
	                "Oversized": get_text(tqs_quote.find('Quote', namespaces), 'Oversized'),
	                "OversizedServiceArea": get_text(tqs_quote.find('Quote', namespaces), 'OversizedServiceArea'),
	                "AbleToCalculate": get_text(tqs_quote.find('Quote', namespaces), 'AbleToCalculate'),
	                "ChargeWeight": get_text(tqs_quote.find('Quote', namespaces), 'ChargeWeight'),
	                "Beyond": get_text(tqs_quote.find('Quote', namespaces), 'Beyond'),
	                "DisplayService": get_text(tqs_quote.find('Quote', namespaces), 'DisplayService'),
	                "TopLine": get_text(tqs_quote.find('Quote', namespaces), 'TopLine'),
	                "UpgradeRequiredForServiceArea": get_text(tqs_quote.find('Quote', namespaces), 'UpgradeRequiredForServiceArea'),
	                "LinkForShipping": get_text(tqs_quote.find('Quote', namespaces), 'LinkForShipping'),
	                "DeliveryDate": get_text(tqs_quote.find('Quote', namespaces), 'DeliveryDate'),
	                "ExtendedTopLine": get_text(tqs_quote.find('Quote', namespaces), 'ExtendedTopLine')
	            },
	            "ShipDate": get_text(tqs_quote, 'ShipDate'),
	            "TariffHeaderID": get_text(tqs_quote, 'TariffHeaderID'),
	            "UserID": get_text(tqs_quote, 'UserID'),
	            "QuoteConfirmationEmail": get_text(tqs_quote, 'QuoteConfirmationEmail'),
	            "DebrisRemoval": get_text(tqs_quote, 'DebrisRemoval'),
	            "Gateway": get_text(tqs_quote, 'Gateway'),
	            "IsInternational": get_text(tqs_quote, 'IsInternational')
	        }
	    }

	    return result


if __name__ == '__main__':
	api = MaerskApi()
	# response = api.find_origin_by_zip('30044')
	# response = api.service_info(sOriginZip='90001', sDestZip='30044')

	response = api.get_new_quote_rest()
	print(f"quote template : {response.text}")
	ratingRootObject = api.xml_to_dict(response.text)

	api.update_rro(ratingRootObject, data)


	# data = {'id': '1234'}
	# result = api.update_quote(response.text, data)
	# print(f"updated quote: {result}")

	# print(response)
