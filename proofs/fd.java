import java.util.concurrent.TimeUnit;
import java.io.*;

class DisplayMessage implements Runnable {
    private String message;

    public DisplayMessage(String message) {
        this.message = message;
    }

    public void run() {
        while(true) {

            File file = new File(message);
            try{
                file.createNewFile();
            FileWriter fw = new FileWriter(file);
            BufferedWriter bw = new BufferedWriter(fw);
            bw.write("Some text here for a reason");
            bw.flush();
            TimeUnit.SECONDS.sleep(2);    
            }
            catch(Exception ex){

            }
            
        }
    }
}

public class fd {

    public static void main(String [] args) {
        Runnable hello = new DisplayMessage("Hello.txt");
        Thread thread1 = new Thread(hello);
        thread1.setName("hello");
        System.out.println("Starting hello thread...");
        thread1.start();

        Runnable bye = new DisplayMessage("Goodbye.txt");
        Thread thread2 = new Thread(bye);
        thread2.setPriority(Thread.MIN_PRIORITY);
        thread2.setName("goodbye");
        System.out.println("Starting goodbye thread...");
        thread2.start();

        while (true) {
            File file = new File("haha.txt");
            try{
                file.createNewFile();
            FileWriter fw = new FileWriter(file);
            BufferedWriter bw = new BufferedWriter(fw);
            bw.write("Some text here for a reason 2");
            bw.flush();
            TimeUnit.SECONDS.sleep(2);
            }
            catch(Exception ex){
                
            }
            
        }
    }
}
