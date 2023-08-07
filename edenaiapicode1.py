# import requests
# import base64
# # un: admin@musey.ai
# # pw: 6"3KTMV_Ej-H#pm
# # Load and encode the local image as base64
# with open('path/to/local/image.jpg', 'rb') as image_file:
#     encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

# # Prepare the API request
# api_url = 'https://api.edenai.run/v1/pretrained/vision/object_detection'
# headers = {
#     'Authorization': 'Bearer YOUR_API_KEY',
#     'Content-Type': 'application/json',
# }

# payload = {
#     'image': encoded_image,
#     'providers': ['google'],
#     'model': 'ssd_mobilenet_v2',
# }

# # Send the API request
# response = requests.post(api_url, headers=headers, json=payload)

# # Process the API response
# if response.status_code == 200:
#     result = response.json()
#     # Extract the detected objects from the response
#     detected_objects = result['predictions']
#     # Process and use the detected objects as required
#     for obj in detected_objects:
#         print(f"Label: {obj['label']}, Confidence: {obj['confidence']}")
# else:
#     print(f"Request failed with status code: {response.status_code}")


N = int(input())
# spaces = ''
# S = N-2
# while S-2 > 0:
#     spaces += ' '
#     S -= 1

# for i in range(N):
#     for j in range(N):
#         if j == 0 or j == N-1:
#             print("*", end='')
#         else:
#             print(end=' ')

#     print()
# spaces = ''
# S = N
# while S > 0:
#     spaces += ' '
#     S -= 1
# for i in range(N):
#     for j in range(N):
#         print("*", end=spaces)
#     print()
# pyramid logic iteration simple
for i in range(N):
    for j in range(i+1):
        print("*", end=' ')
    print()
