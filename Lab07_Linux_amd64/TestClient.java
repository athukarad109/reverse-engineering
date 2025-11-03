import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

import java.net.Socket;
import java.util.Arrays;


public class TestClient {
    public static void main(String[] args) {
    	try {
    		new TestClientUnitTests(args[0], Integer.parseInt(args[1])).run();
    	}
    	catch (IOException e) {
    		throw new RuntimeException("Something went horribly wrong", e);
    	}
    }
    
    private Socket s;
    private InputStream in;
    private OutputStream out;

	byte[] data = new byte[1];
	
	private void printBytes(byte[] d) {
		System.out.print(":");
		for (byte b: d) {
			String h = "0" + Integer.toHexString(b);
			h = h.substring(h.length() - 2);
			System.out.print(h);
		}
		System.out.println();
	}
	
    private void sendByte(int val) throws IOException {
    	// Oiy, Java.
    	val = val % 256;
    	if (val >= 128) {
    		val-= 256;
    	}
    	data[0] = (byte) val;
    	out.write(data);
    }
    
    private void sendShort(int val) throws IOException {
    	// Have to hack for little endian in Java
    	sendByte(val);
    	val>>= 8;
    	sendByte(val);
    }
    
    private void sendData(byte[] d) throws IOException {
    	out.write(d);
    }
    
    private int recvByte() throws IOException {
    	in.read(data);
    	int val = data[0];
    	if (val < 0) {
    		val+= 256;
    	}
    	return val;
    }
    
    private int recvShort() throws IOException {
    	int val = recvByte();
    	val|= recvByte() << 8;
    	return val;
    }
    
    public TestClient(String addr, int port) throws IOException {
    	s = new Socket(addr, port);
    	in = s.getInputStream();
    	out = s.getOutputStream();
    	
    	int resp = recvByte();
    	if (resp != 5) {
    		throw new ClientException("Unexpected message: " + resp);
    	}
    }
    
    public void authenticate(String user, String password) throws IOException {
    	byte[] userBytes = user.getBytes();
    	byte[] passBytes = password.getBytes();
    	
    	try {
	    	sendByte(0);
	    	sendShort(userBytes.length + 1);
	    	sendData(userBytes);
	    	sendByte(0); // Null terminator
    	}
    	catch (IOException e) {
    	}
    	
    	int resp = recvByte();
    	if (resp != 6) {
    		throw new ClientException("Unexpected message: " + resp);
    	}
    	byte[] userBack = new byte[userBytes.length];
    	in.read(userBack);
    	resp = recvByte(); // Null terminator
    	if (resp != 0 || !Arrays.equals(userBytes, userBack)) {
    		throw new ClientException("Username response mismatch: '" + new String(userBack) + "', terminator = " + resp);
    	}
    	
    	try {
	    	sendByte(2);
	    	sendShort(passBytes.length + 1);
	    	out.write(passBytes);
	    	sendByte(0); // Null terminator
    	}
    	catch (IOException e) {
    	}
    	
    	resp = recvByte();
    	if (resp != 8) {
    		throw new ClientException("Access denied");
    	}
    }
    
    public void setSecret(String secret) throws IOException {
    	byte[] secretBytes = secret.getBytes();
    	try {
	    	sendByte(3);
	    	sendShort(secretBytes.length + 1);
	    	sendData(secretBytes);
	    	sendByte(0);
    	}
    	catch (IOException e) {
    	}
    	
    	int resp = recvByte();
    	if (resp != 9) {
    		throw new ClientException("Unexpected message: " + resp);
    	}
    }
    
    public String getSecret() throws IOException {
    	return getSecret(0xffff);
    }
    
    public String getSecret(int length) throws IOException {
    	byte[] secretBytes = new byte[length];
    	
    	try {
	    	sendByte(4);
	    	sendShort(length);
    	}
    	catch (IOException e) {
    	}
    	
    	int resp = recvByte();
    	if (resp != 10) {
    		throw new ClientException("Unexpected message: " + resp);
    	}
    	in.read(secretBytes);
    	int i = 0;
    	for (i = 0; i < secretBytes.length && secretBytes[i] != 0; i++);
    	return new String(secretBytes, 0, i);
    }
    
    public void close() throws IOException {
    	s.close();
    }
    
    @Override
    public void finalize() throws IOException {
    	close();
    }
}

class ClientException extends RuntimeException {
	public ClientException(String message, Throwable cause) {
		super(message, cause);
	}
	
	public ClientException(String message) {
		this(message, null);
	}
}

class TestClientUnitTests {
	final String ADDR;
	final int PORT;
	
	public TestClientUnitTests(String addr, int port) {
		this.ADDR = addr;
		this.PORT = port;
	}
	
	public void testSetNoAuth() throws IOException {
		TestClient t = new TestClient(ADDR, PORT);
		try {
			t.setSecret("This secret should never be stored");
			throw new AssertionError("testSetNoAuth failed");
		}
		catch (ClientException e) {
			System.err.println("testSetNoAuth passed: " + e);
		}
	}
	
	public void testGetNoAuth() throws IOException {
		TestClient t = new TestClient(ADDR, PORT);
		try {
			String data = t.getSecret();
			throw new AssertionError("testGetNoAuth failed");
		}
		catch (ClientException e) {
			System.err.println("testGetNoAuth passed: " + e);
		}
	}
	
	public void testAuthBad() throws IOException {
		TestClient t = new TestClient(ADDR, PORT);
		try {
			t.authenticate("bob", "wrongpass");
			throw new AssertionError("testAuthBad failed");
		}
		catch (ClientException e) {
			System.err.println("testAuthBad passed: " + e);
		}
	}
	
	public void testAuthGood() throws IOException {
		TestClient t = new TestClient(ADDR, PORT);
		try {
			t.authenticate("johndoe", "password");
			System.err.println("testAuthGood passed");
		}
		catch (ClientException e) {
			throw new AssertionError("testAuthGood failed", e);
		}
	}
	
	final static String TEST_SECRET = "This is a really good secret";
	
	public void testSetAuth() throws IOException {
		TestClient t = new TestClient(ADDR, PORT);
		t.authenticate("johndoe", "password");
		try {
			t.setSecret(TEST_SECRET);
			System.err.println("testSetAuth passed");
		}
		catch (ClientException e) {
			throw new AssertionError("testSetAuth failed", e);
		}
	}
	
	public void testGetAuth() throws IOException {
		TestClient t = new TestClient(ADDR, PORT);
		t.authenticate("johndoe", "password");
		try {
			String secret = t.getSecret();
			if (secret.equals(TEST_SECRET)) {
				System.err.println("testGetAuth passed");
			} else {
				throw new AssertionError("testGetAuth failed: secret does not match: '" + secret + "' (" + secret.length() + ")");
			}
		}
		catch (ClientException e) {
			throw new AssertionError("testGetAuth failed", e);
		}
	}
	
	public void run() throws IOException {
		testSetNoAuth();
		testGetNoAuth();
		testAuthBad();
		testAuthGood();
		testSetAuth();
		testGetAuth();
		System.err.println("All tests passed successfully");
	}
}
