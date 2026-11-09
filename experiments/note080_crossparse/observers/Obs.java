// note080 Java observer: Double.parseDouble and BigDecimal.doubleValue on each token (one per line).
// Same output format as obs_python.py. The JDK has no built-in JSON parser.
import java.math.BigDecimal;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

public class Obs {
    public static void main(String[] args) throws Exception {
        List<String> toks = Files.readAllLines(Path.of(args[0]));
        System.out.println("#versions\t{\"java\": \"" + System.getProperty("java.version") + "\"}");
        for (int i = 0; i < toks.size(); i++) {
            try {
                double v = Double.parseDouble(toks.get(i));
                System.out.printf("java-Double.parseDouble\t%d\tOK\t%016x%n", i, Double.doubleToRawLongBits(v));
            } catch (Exception e) {
                System.out.printf("java-Double.parseDouble\t%d\tERR\t%s%n", i, e.getClass().getSimpleName());
            }
        }
        for (int i = 0; i < toks.size(); i++) {
            try {
                double v = new BigDecimal(toks.get(i)).doubleValue();
                System.out.printf("java-BigDecimal\t%d\tOK\t%016x%n", i, Double.doubleToRawLongBits(v));
            } catch (Exception e) {
                System.out.printf("java-BigDecimal\t%d\tERR\t%s%n", i, e.getClass().getSimpleName());
            }
        }
    }
}
