import java.net.*; 
import java.io.*; 
import java.util.concurrent.TimeUnit;  
class Client 
{ 
    // initialize socket and input output streams 
    private Socket socket            = null; 
    private DataInputStream  input   = null; 
    private DataOutputStream out     = null; 
  
    // constructor to put ip address and port 
    public Client(String urlToRead) 
    { 
     try{
      StringBuilder result = new StringBuilder();
      URL url = new URL(urlToRead);
      HttpURLConnection conn = (HttpURLConnection) url.openConnection();
      conn.setRequestMethod("GET");
      BufferedReader rd = new BufferedReader(new InputStreamReader(conn.getInputStream()));
      String line;
      while ((line = rd.readLine()) != null) {
         result.append(line);
      }
      rd.close();  
     }
     catch(Exception ex){
        
     }
      
      
} 
}
//Client client = new Client("172.217.167.174", 80); 

class DisplayMessage implements Runnable {
    private String message;

    public DisplayMessage(String message) {
        this.message = message;
    }

    public void run() {
        while(true) {

            try{
            Client client = new Client(message); 
            TimeUnit.SECONDS.sleep(1);    
            }
            catch(Exception ex){

            }
            
        }
    }
}

public class tcp {

    public static void main(String [] args) {
        Runnable hello = new DisplayMessage("https://www.google.com");
        Thread thread1 = new Thread(hello);
        thread1.setName("hello");
        System.out.println("Starting hello thread...");
        thread1.start();

        Runnable bye = new DisplayMessage("https://www.facebook.com");
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
