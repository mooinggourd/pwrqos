package pwrqos.metrics;

import javax.jws.WebMethod;
import javax.jws.WebService;
import javax.xml.soap.MessageFactory;
import javax.xml.soap.SOAPBody;
import javax.xml.soap.SOAPConnection;
import javax.xml.soap.SOAPConnectionFactory;
import javax.xml.soap.SOAPElement;
import javax.xml.soap.SOAPEnvelope;
import javax.xml.soap.SOAPException;
import javax.xml.soap.SOAPMessage;

@WebService
public class HelloMetrics {
	private SOAPConnection connection;
	private SOAPMessage message;
	private SOAPEnvelope envelope;
	private SOAPBody body;
	private SOAPElement bodyElement;
	
	@WebMethod
	public boolean measureAvailability(
			String wsdlURI,
			String serviceName,
			String methodName,
			String serviceNameSpace ) throws Exception {
		try {
			// Create new message
			message = MessageFactory.newInstance().createMessage();
			
			// Get the envelope of the message
			envelope = message.getSOAPPart().getEnvelope();
			
			// Get the body of the message
			body = message.getSOAPBody();
			// Create message content
			bodyElement = body.addBodyElement(envelope.createName(methodName, "ns1", serviceNameSpace));
			
			// Create osoba and save message
			createOsoba();			
			   
	        System.out.println("\nRequest:\n");  
	        message.writeTo(System.out);  
	        System.out.println(); 
	        
	        // Create new connection and send message
	     	connection = SOAPConnectionFactory.newInstance().createConnection();
	        SOAPMessage reply = connection.call(message, wsdlURI);
	        
	        System.out.println("\nResponse:\n");  
	        reply.writeTo(System.out);  
	        System.out.println();
	        
	        connection.close();
	        
	        if (reply.getSOAPBody().getFault() != null) {
	        	return false;
	        }
	        
		} catch (Exception e) {
			e.printStackTrace();
			return false;
		}
        
		return true;
		
	}
	
	@WebMethod
	public double measureRunningTime(
			String wsdlURI,
			String serviceName,
			String methodName,
			String serviceNameSpace ) throws Exception {
		try {
			// Create new message
			message = MessageFactory.newInstance().createMessage();
			
			// Get the envelope of the message
			envelope = message.getSOAPPart().getEnvelope();
			
			// Get the body of the message
			body = message.getSOAPBody();
			// Create message content
			bodyElement = body.addBodyElement(envelope.createName(methodName, "ns1", serviceNameSpace));
			
			// Create osoba and save message
			createOsoba();  
			   
	        System.out.println("\nRequest:\n");  
	        message.writeTo(System.out);  
	        System.out.println(); 
	        
	        long startTime = System.nanoTime();
	        
	        // Create new connection and send message
	     	connection = SOAPConnectionFactory.newInstance().createConnection();
	        SOAPMessage reply = connection.call(message, wsdlURI);
	        
	        long endTime = System.nanoTime();
	        
	        System.out.println("\nResponse:\n");  
	        reply.writeTo(System.out);  
	        System.out.println();
	        
	        connection.close();
	        
	        if (reply.getSOAPBody().getFault() != null) {
	        	throw new Exception("Tested method returned a fault exception.");
	        }
	        
	        return (double)(endTime - startTime) / 1000000.0;
	        
		} catch (Exception e) {
			throw e;
		}
	}
	
	private SOAPElement createOsoba() {
		SOAPElement osoba = null;
		try {
			osoba = bodyElement.addChildElement(envelope.createName("os"));
			osoba.addChildElement("imie").addTextNode("Imie");
			osoba.addChildElement("nazwisko").addTextNode("Nazwisko");
			SOAPElement adres = osoba.addChildElement(envelope.createName("adres"));
				adres.addChildElement("ulicat").addTextNode("NazwaUlicy");
				adres.addChildElement("nr").addTextNode("0");
				SOAPElement miasto = adres.addChildElement(envelope.createName("miasto"));
					miasto.addChildElement("nazwa_miasta").addTextNode("NazwaMiasta");
					miasto.addChildElement("kod_pocztowy").addTextNode("KodPocztowy");
			
			message.saveChanges();
		} catch (SOAPException e) {
			e.printStackTrace();
		}
		return osoba;
		
	}
}
