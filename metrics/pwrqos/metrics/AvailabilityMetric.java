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
public class AvailabilityMetric {
	// SOAP elements
	private SOAPConnection connection;
	private SOAPMessage message;
	private SOAPEnvelope envelope;
	private SOAPBody body;
	private SOAPElement bodyElement;
	
	public AvailabilityMetric() {
		super();
	}
	
	@WebMethod
	public boolean measureAvailability(
			String wsdlURI,
			String serviceName,
			String methodName,
			String serviceNameSpace ) throws SOAPException {
		try {
			message = MessageFactory.newInstance().createMessage();
			
			envelope = message.getSOAPPart().getEnvelope();
			
			body = message.getSOAPBody();
			bodyElement = body.addBodyElement(envelope.createName(methodName, "ns1", serviceNameSpace));
			bodyElement.addChildElement("number1").addTextNode("2");
			bodyElement.addChildElement("number2").addTextNode("4");
					
			message.saveChanges();  
			   
	        System.out.println("\nRequest:\n");  
	        message.writeTo(System.out);  
	        System.out.println(); 
	        
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
}
