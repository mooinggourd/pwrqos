package pwrqos.metrics;

import javax.jws.WebService;
import javax.jws.WebMethod;
import javax.xml.soap.MessageFactory;
import javax.xml.soap.SOAPBody;
import javax.xml.soap.SOAPConnection;
import javax.xml.soap.SOAPConnectionFactory;
import javax.xml.soap.SOAPElement;
import javax.xml.soap.SOAPEnvelope;
import javax.xml.soap.SOAPMessage;
import javax.xml.soap.SOAPPart;

@WebService()
public class RunningTimeMetric {

    public RunningTimeMetric() {}

    @WebMethod()
    public double measureRunningTime(
        String serviceName,
        String wsdlURI,
        String methodLocalName,
        String methodNamespaceUri) throws Exception
    {                    	
		SOAPConnectionFactory soapConnFactory = SOAPConnectionFactory.newInstance();     		
		SOAPConnection connection = soapConnFactory.createConnection();  

        // utwórz wiadomość  
        MessageFactory messageFactory = MessageFactory.newInstance();
        SOAPMessage message = messageFactory.createMessage();  
  
        SOAPPart soapPart = message.getSOAPPart();  
        SOAPEnvelope envelope = soapPart.getEnvelope();  
  
        // dodaj treść wiadomości  
        SOAPBody body = envelope.getBody();    	             
        SOAPElement bodyElement = body.addChildElement(envelope.createName(methodLocalName, "ns1", methodNamespaceUri));   
  
        bodyElement.addChildElement("number1").addTextNode("10");
        bodyElement.addChildElement("number2").addTextNode("15");
        
        message.saveChanges();  
   
        System.out.println("\nRequest:\n");  
        message.writeTo(System.out);  
        System.out.println();  
    
        long startTime = System.nanoTime();

        // wywołaj testowaną metodę        
        SOAPMessage reply = connection.call(message, wsdlURI);          
        
        long endTime = System.nanoTime();

        if (reply.getSOAPBody().getFault() != null)
        {
        	throw new Exception("Tested method returned a fault exception.");
        }
        
        System.out.println("\nResponse:\n");  
        reply.writeTo(System.out);  
        System.out.println();    
  
        connection.close();
        
        // zamień na milisekundy (1ms = 10^6ns)
        return (double)(endTime - startTime) / 1000000.0;            	
    }    

} 
