using UnityEngine;
using System;
using System.Collections;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;

namespace KartGame.KartSystems
{

    public class KeyboardInput : BaseInput
	{
        public string Horizontal = "Horizontal";
        public string Vertical = "Vertical";

        Thread receiveThread;
		UdpClient client;
		int port;

		public GameObject Player;
		float angleDeg = 0;

		public float x_recebido = 0;
		public float y_recebido = 0;

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


					int f1 = BitConverter.ToInt32(data, 0);
                    int f2 = BitConverter.ToInt32(data, 4);

					//Debug.Log(f1 + "Valor X");
					//Debug.Log(f2 + "Valor Y");

					Vector2 v1 = new Vector2(f1, f2);

					//Debug.Log(v1 + "Valor do angulo");

					float angulo = Vector2.Dot(v1.normalized, Vector2.right);

					x_recebido = 0;
					y_recebido = 0;

					if(Math.Abs(f1) > 0)
                    {
						y_recebido = 1;
                    }

					if (!(angulo >= -0.25f && angulo <= 0.25f))
                    {
						x_recebido = angulo/2;
						y_recebido = 1;
					}  
			
					Debug.Log(x_recebido + "Valor recebido");

				}
				catch (Exception e)
				{
					print(e.ToString());
				}
			}
		}

        public override Vector2 GenerateInput()
        {
            return new Vector2
            {
                x = x_recebido,//Input.GetAxis(Horizontal),
                y = y_recebido//Input.GetAxis(Vertical)
			};
        }

		void OnApplicationQuit()
		{
			receiveThread.Abort();
			client.Close();
		}
	}
}
