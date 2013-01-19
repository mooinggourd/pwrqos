import javax.xml.ws.Endpoint;
import pwrqos.metrics.RunningTimeMetric;

public class RunningTimeMetricPublisher {
    public static final String serviceUrl = "http://localhost:9999/ws/runningtime"; 

    public static void main(String[] args) {
        Endpoint.publish(serviceUrl, new RunningTimeMetric());
    }
}
