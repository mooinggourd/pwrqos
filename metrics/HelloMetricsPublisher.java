import pwrqos.metrics.HelloMetrics;
import javax.xml.ws.Endpoint;

public class HelloMetricsPublisher {
	public static final String serviceUrl = "http://localhost:9996/ws/availability"; 

    public static void main(String[] args) {
        Endpoint.publish(serviceUrl, new HelloMetrics());
    }
}
