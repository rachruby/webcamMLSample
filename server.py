from fastapi import FastAPI, WebSocket, WebSocketDisconnect

import cv2
import numpy as np
from PIL import Image
from io import BytesIO

app = FastAPI()

def process_image(image: np.ndarray) -> int :
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False

    #Create detect
    results = pose.process(image)

    #Recolor back to BGR
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    #Extract landmark
    try: 
        landmarks = results.pose_landmarks.landmark
        
        shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
        elbow = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        wrist = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]

        #Calculate angle
        angle = calculate_angle(shoulder, elbow, wrist)

        #Visualize 
        cv2.putText(image, str(angle),
                    tuple(np.multiply(elbow, [640, 480]).astype(int)), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                        
                    )

        #jumping jack counter logic 
        if angle > 160:
            stage = "down"
        if angle < 30 and stage == 'down':
            stage = "up"
            counter += 1
            print (counter)
    except: 
        pass

    # render jumping jack counter
    # setup status box
    cv2.rectangle(image, (0,0), (300,150), (245, 117, 16), -1)

    # rep data
    cv2.putText(image, 'REPS', (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(image, str(counter), (20,130), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)

    # Stage data
    cv2.putText(image, 'STAGE', (200, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, stage, (180,130), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)  

    #drawingSpec is the specification of drawing a landmark
    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS, 
                                mp_drawing.DrawingSpec(color = (245, 117, 66), thickness = 2, circle_radius = 2), 
                                mp_drawing.DrawingSpec(color=(245, 66, 230), thickness = 2, circle_radius = 2))
 
 def processimage(image: np.ndarray) -> int:
    # Your image processing and number calculation logic here
    # For simplicity, let's return the average pixel intensity
    return int(np.mean(image))

@app.websocket("/ws")
async def websocketendpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receivebytes()
            # Convert the bytes data to a numpy array for image processing
            image = np.array(Image.open(BytesIO(data)))
            # Process the image and calculate a number
            result = processimage(image)
            # Send the result back to the client
            await websocket.send_text(str(result))
    except WebSocketDisconnect:
        print("Client disconnected")

if __name == "__main":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
