import javax.xml.ws.Endpoint;
import pwrqos.metrics.AvailabilityMetric;

public class AvailabilityMetricPublisher {
	public static final String serviceUrl = "http://localhost:9997/ws/availability"; 

    public static void main(String[] args) {
        Endpoint.publish(serviceUrl, new AvailabilityMetric());
    }
}
