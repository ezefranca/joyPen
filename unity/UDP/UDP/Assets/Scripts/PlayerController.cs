using UnityEngine;
using System;
using System.Collections;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;

public class PlayerController : MonoBehaviour
{
	Thread receiveThread;
	UdpClient client;
	int port;

	public GameObject Player;
	float angleDeg = 0;

	void Start()
	{
		port = 5065;
		InitUDP(); 
	}

	private void InitUDP()
	{
		print("UDP Inicializado");

		receiveThread = new Thread(new ThreadStart(ReceiveData));
		receiveThread.IsBackground = true; 
		receiveThread.Start();

	}

	private void ReceiveData()
	{
		client = new UdpClient(port);
		while (true)
		{
			try
			{
				IPEndPoint anyIP = new IPEndPoint(IPAddress.Parse("0.0.0.0"), port);
				byte[] data = client.Receive(ref anyIP);
				string text = Encoding.UTF8.GetString(data);
				angleDeg = float.Parse(text);
				print("angulo recebido em graus " + angleDeg);
			}
			catch (Exception e)
			{
				print(e.ToString());
			}
		}
	}

	// 6. Check for variable value, and make the Player Jump!
	void Update()
	{
		print(angleDeg);
		Vector3 to = new Vector3(angleDeg, 0, 0);
		Player.transform.eulerAngles = Vector3.Lerp(Player.transform.rotation.eulerAngles, to, Time.deltaTime);
	}

	void OnApplicationQuit()
	{
		receiveThread.Abort();
		client.Close();
	}
}
