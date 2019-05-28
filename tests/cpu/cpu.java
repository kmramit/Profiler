import java.util.concurrent.TimeUnit;
import java.io.*;

class DisplayMessage implements Runnable {
    private String message;

    public DisplayMessage(String message) {
        this.message = message;
    }

    public void run() {
        while(true) {

            this.message = "override";
            
        }
    }
}

public class cpu {

    public static void main(String [] args) {
        Runnable hello = new DisplayMessage("A");
        Thread thread1 = new Thread(hello);
        thread1.setName("hello");
        System.out.println("Starting hello thread...");
        thread1.start();

        Runnable bye = new DisplayMessage("B");
        Thread thread2 = new Thread(bye);
        thread2.setName("goodbye");
        System.out.println("Starting goodbye thread...");
        thread2.start();

        while(true){
            String message = "C";
        }
    }
}
