from dataclasses import dataclass, field
from urllib.parse import urljoin, urlencode
from dotenv import load_dotenv
import zeep
from zeep.transports import Transport
import ssl
import requests
import xml.etree.ElementTree as ET
import os
import json
import logging
from datetime import datetime

# logging.basicConfig(level=logging.DEBUG)
load_dotenv()


@dataclass
class MaerskApi():
	base_api_url: str = 'https://pilotws.pilotdelivers.com'
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

	def get_new_shipment(self):
		# Disable SSL warnings if you're setting verify=False
		requests.packages.urllib3.disable_warnings()

		# Create a session
		session = requests.Session()
		session.headers.update({
			"Content-Type": "application/soap+xml; charset=utf-8"
		})
		session.verify = False  # Disable SSL verification if needed

		# Set up Zeep client
		wsdl_url = "https://ws3.pilotdelivers.com/webservice/wsshipments/Shipment.asmx?WSDL"
		settings = zeep.Settings(strict=False)
		transport = Transport(session=session)
		client = zeep.Client(wsdl=wsdl_url, transport=transport, settings=settings)

		# Call GetNewShipment
		try:
			response = client.service.GetNewShipment()
			# Check the full response
			print(response)

			# Extract the actual data from _value_1 if it exists
			if hasattr(response, 'GetNewShipmentResult'):
				shipment_result = response.GetNewShipmentResult
				if hasattr(shipment_result, '_value_1'):
					print(shipment_result._value_1)
				else:
					print("No _value_1 in GetNewShipmentResult")
			else:
				print("No GetNewShipmentResult in response")

		except Exception as e:
			print("Error:", e)

	def get_new_shipment_rest(self):
		url = "https://ws3.pilotdelivers.com/webservice/wsshipments/Shipment.asmx"
		headers = {
			"Content-Type": "application/soap+xml; charset=utf-8",
			"SOAPAction": "http://tempuri.org/GetNewShipment"
		}

		# SOAP envelope as per documentation
		soap_envelope = """<?xml version="1.0" encoding="utf-8"?>
			<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
			xmlns:xsd="http://www.w3.org/2001/XMLSchema"
			xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
				<soap12:Body>
					<GetNewShipment xmlns="http://tempuri.org/" />
				</soap12:Body>
			</soap12:Envelope>
		"""

		response = requests.post(url, data=soap_envelope, headers=headers, verify=False)

		return response

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

	def get_rating_rest(self, ratingRootObject, data):
		ratingRootObject['Rating']['LocationID'] = data['LocationID']
		ratingRootObject['Rating']['Shipper']['Zipcode'] = data['Shipper']['Zipcode']
		ratingRootObject['Rating']['Consignee']['Zipcode'] = data['Consignee']['Zipcode']
		ratingRootObject['Rating']['LineItems'] = data['LineItems']
		ratingRootObject['Rating']['TariffHeaderID'] = data['TariffHeaderID']

		endpoint = 'https://www.pilotssl.com/pilotapi/v1/Ratings'

		# payload = json.dumps(ratingRootObject)
		# encoded_payload = urlencode(payload)
		# content_length = str(len(encoded_payload))
		payload = ratingRootObject

		headers = {
			'Content-Type': 'application/json',
			'Accept': 'text/plain',
			'api-key': os.getenv('P_MAERSK_API_KEY')
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

	def quote_to_dict(self, xml_string):
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

	def shipment_to_dict(self, xml_string):
		# Parse the XML string
		root = ET.fromstring(xml_string)

		# Define the namespaces
		namespaces = {
			'soap': 'http://www.w3.org/2003/05/soap-envelope',
			'diff': 'urn:schemas-microsoft-com:xml-diffgram-v1',
			'ds': 'http://tempuri.org/dsShipment.xsd'
		}

		# Navigate to dsShipment elements
		diffgram = root.find('.//diff:diffgram', namespaces)
		ds_shipment = diffgram.find('.//ds:dsShipment', namespaces)

		if ds_shipment is None:
			raise ValueError("ds_shipment element not found in the XML.")

		# Helper function to extract text from an element
		def get_text(element, tag):
			if element is None:
				return ''
			child = element.find(tag, namespaces)

			return child.text if child is not None else ''

		result = {
			"Shipment": {
				"QuoteId": "string",
				"LocationId": "string",
				"TransportByAir": "string",
				"IATA_Classifications": "string",
				"PackingContainers": "string",
				"DeclaredValue": "string",
				"COD": "string",
				"TariffId": "string",
				"TariffName": "string",
				"TariffCode": "string",
				"Notes": "string",
				"Service": "string",
				"AirtrakServiceCode": "string",
				"TariffExtension": "string",
				"QuoteDate": "string",
				"HoldAtAirport": "string",
				"ControlStation": "string",
				"ProNumber": "string",
				"ConsigneeAttn": "string",
				"ThirdPartyAuth": "string",
				"ShipperRef": "string",
				"ConsigneeRef": "string",
				"DeliveryDate": "string",
				"AmountDueConsignee": "string",
				"ShipDate": "2025-02-02T21:30:11.261Z",
				"OverSized": "string",
				"PayType": "string",
				"POD": "string",
				"SatDelivery": "string",
				"SpecialInstructions": "string",
				"ReadyTime": "2025-02-02T21:30:11.261Z",
				"CloseTime": "2025-02-02T21:30:11.261Z",
				"HomeDelivery": "string",
				"ShipmentId": "string",
				"LockDate": "string",
				"LockUser": "string",
				"LastUpdate": "2025-02-02T21:30:11.261Z",
				"AddressId": "string",
				"Platinum": "string",
				"IsShipper": "string",
				"GBL": "string",
				"IsInsurance": "string",
				"Condition": "string",
				"Packaging": "string",
				"TariffHeaderId": "string",
				"ProductName": "string",
				"ProductDescription": "string",
				"DebrisRemoval": "string",
				"IsScreeningConsent": "string",
				"EmailBOL": "string",
				"ServiceName": "string",
				"Hazmat": "string",
				"HazmatNumber": "string",
				"HazmatClass": "string",
				"HazmatPhone": "string",
				"IsDistribution": "string",
				"DeliveryStartTime": "string",
				"AirtrakQuoteNo": "string",
				"Shipper": {
					"ShipmentId": "string",
					"Name": "string",
					"Address1": "string",
					"Address2": "string",
					"Address3": "string",
					"City": "string",
					"State": "string",
					"Zipcode": "string",
					"Country": "string",
					"Airport": "string",
					"Owner": "string",
					"Attempted": "string",
					"PrivateRes": "string",
					"Hotel": "string",
					"InsIde": "string",
					"Liftgate": "string",
					"TwoManHours": "string",
					"WaitTimeHours": "string",
					"Special": "string",
					"DedicatedVehicle": "string",
					"Miles": "string",
					"Canadian": "string",
					"ServiceCode": "string",
					"Convention": "string",
					"Contact": "string",
					"Phone": "string",
					"Extension": "string",
					"Email": "string",
					"SendEmail": "string"
				},
				"Consignee": {
					"ShipmentId": "string",
					"Name": "string",
					"Address1": "string",
					"Address2": "string",
					"Address3": "string",
					"City": "string",
					"State": "string",
					"Zipcode": "string",
					"Country": "string",
					"Airport": "string",
					"Owner": "string",
					"Attempted": "string",
					"PrivateRes": "string",
					"Hotel": "string",
					"InsIde": "string",
					"Liftgate": "string",
					"TwoManHours": "string",
					"WaitTimeHours": "string",
					"Special": "string",
					"DedicatedVehicle": "string",
					"Miles": "string",
					"Canadian": "string",
					"ServiceCode": "string",
					"Convention": "string",
					"Contact": "string",
					"Phone": "string",
					"Extension": "string",
					"Email": "string",
					"SendEmail": "string"
				},
				"ThirdParty": {
					"ShipmentId": "string",
					"Name": "string",
					"Address1": "string",
					"Address2": "string",
					"Address3": "string",
					"City": "string",
					"State": "string",
					"Zipcode": "string",
					"Country": "string",
					"Contact": "string",
					"Phone": "string",
					"Extension": "string",
					"Email": "string",
					"SendEmail": "string"
				},
				"LineItem": [
					{
						"ShipmentId": "string",
						"LineRow": 0,
						"PackageType": "string",
						"Pieces": 0,
						"Weight": 0,
						"Description": "string",
						"Length": 0,
						"Width": 0,
						"Height": 0,
						"Kilos": 0
					}
				],
				"Quote": {
					"ShipmentId": "string",
					"Service": "string",
					"DimWeight": "string",
					"TotalQuote": "string",
					"Oversized": "string",
					"AbleToCalculate": "string",
					"ChargeWeight": "string",
					"Beyond": "string",
					"DisplayService": "string",
					"TopLine": "string",
					"UpgradeRequiredForServiceArea": "string",
					"LinkForShipping": "string",
					"Breakdown": {
						"ShipmentId": "string",
						"ChargeCode": "string",
						"Charge": "string",
						"BillCodeName": "string"
					}
				},
				"InternationalServices": {
					"ShipmentId": "string",
					"ShipmentType": "string",
					"Service": "string",
					"Incoterms": "string",
					"CustomsValue": "string"
				},
				"International": {
					"ShipmentId": "string",
					"USPPI_EIN": "string",
					"PartiesToTransaction": "string",
					"IntermediateConsignee": "string",
					"MethodOfTransportation": "string",
					"ConsolIdateOrDirect": "string",
					"ShipmentReferenceNumber": "string",
					"EntryNumber": "string",
					"InBondCode": "string",
					"RoutedExportTransaction": "string",
					"LicenseNumber": "string",
					"ECCN": "string",
					"HazMat": "string",
					"LicenseValue": "string",
					"InBondCodeValue": "string",
					"MethodOfTransportationValue": "string"
				},
				"OtherReferences": [
					{
						"ShipmentId": "string",
						"Reference": "string",
						"ReferenceType": "string"
					}
				],
				"ScheduleBLines": {
					"ScheduleBId": "string",
					"ShipmentId": "string",
					"ScheduleBLine": "string",
					"DForM": "string",
					"ScheduleBNumber": "string",
					"Quantity": "string",
					"Weight": "string",
					"VinNumber": "string",
					"DollarValue": "string",
					"ScheduleBCode": "string"
				},
				"ShipmentCustomerInfo": {
					"User_Email": "string",
					"User_Name": "string",
					"User_Phone": "string",
					"Name": "string",
					"Address1": "string",
					"Address2": "string",
					"City": "string",
					"State": "string",
					"Zip": "string",
					"Country": "string"
				}
			}
		}

		return result


if __name__ == '__main__':
	api = MaerskApi()
	# response = api.find_origin_by_zip('30044')
	# response = api.service_info(sOriginZip='90001', sDestZip='30044')

	# response = api.get_new_quote()
	# response = api.get_new_quote_rest()
	# print(f"quote template : {response.text}")
	# ratingRootObject = api.xml_to_dict(response.text)

	# Sample Data
	# data = {
	# 	"LocationID": os.getenv('LOCATIONID'),
	# 	"Shipper": {
	# 		"Zipcode": "90001"
	# 	},
	# 	"Consignee": {
	# 		"Zipcode": "30044"
	# 	},
	# 	"LineItems": [
	# 		{
	# 			"Pieces": "1",
	# 			"Weight": "1",
	# 			"Description": "ride on car toys",
	# 			"Length": "1",
	# 			"Width": "1",
	# 			"Height": "1"
	# 		}
	# 	],
	# 	"TariffHeaderID": os.getenv('TARIFFHEADERID')
	# }

	# response = api.get_rating_rest(ratingRootObject, data)

	# data = {'id': '1234'}
	# result = api.update_quote(response.text, data)
	# print(f"updated quote: {result}")

	response = api.get_new_shipment_rest()
	# result = api.shipment_to_dict(response.content)

	print(response.text)
