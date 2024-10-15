import json
from openai import OpenAI # type: ignore
from PIL import Image
import base64
import io
import os
import pandas as pd



def image_to_bytes(image_wrapper):

    # Create a bytes bufferpy
    img_byte_array = io.BytesIO()
    
    # Save the ImageWrapper object to the buffer
    image_wrapper.save(img_byte_array, format='jpeg')  # Specify format if needed, e.g., 'JPEG', 'PNG', etc.
    
    # Retrieve byte data
    img_bytes = img_byte_array.getvalue()
    
    return img_bytes


# Create a function that resizes the image
def resize_image(image_wrapper, width, height):
    
    # Resize the image
    resized_image = image_wrapper.resize((width, height))
    
    return resized_image

# Create a function that converts an image to a base64 string
# what type is image_wrapper
def image_to_base64(image_wrapper):

    # Convert the image to bytes
    img_bytes = image_to_bytes(image_wrapper)
    
    # Encode the bytes to base64
    b64_image_string = base64.b64encode(img_bytes)
    
    return b64_image_string


# Create a function that reads in an image

 # My image is a 200x374 jpeg that is 102kb large
  
# foo = Image.open(r'C:\Users\benji\Downloads\309 Hirsch\Demo\IMG_1645.jpg')
 
 # foo = foo.resize((160,300),Image.LANCZOS)
# foo = foo.thumbnail(size=(200, 200))


"""
image_bytes = image_to_bytes(foo)

b64_ImageString = base64.b64encode(image_bytes)

"""


def call_openai_api(b64_ImageString):
    # read the api key from the API_Key file
    API_KEY = open("API_Key", "r").read()
    OpenAI.api_key = API_KEY

    client = OpenAI(api_key = API_KEY)

    response = client.chat.completions.create(
      model="gpt-4o",
      messages=[
        {
          "role": "system", "content":"You are an assistant who is great at estimating the price of an item and finds the most expensive item",         
          "role": "user",
          "content": [
            {"type": "text", "text": "Return in machine readable JSON the name, model, retail price, and the website the product can be found. If you can't find the exact information summarize, then find a similar product and format the output the same way.  If you can't find any information about the image, then summarize that in the name section place and a 0 in the price section of the JSON response.\n\nOutput should be in machine readable JSON format like: \n{\nName:abc,\nModel:xyz,\nPrice: 1,\nwebsite:https://www.target.com\n}If you can't find a price for the product, place an estimate in the retail_price section. Never return with 0 retail_price"},
            {
              "type": "image_url",
              "image_url": {
                "url": "data:image/jpeg;base64, " + b64_ImageString.decode('utf-8'),
                "detail":"high"
              },
            },
          ],
        }
      ],
      temperature=0.52,
      max_tokens=4095,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0,
      response_format={
          "type":"json_object"
      }

    )
    return response


# Create a function to read all images from a directory
def read_images_from_directory(directory_path):
    # Create a list to store the images
    images = []
    
    # Loop through all the files in the directory
    for file in os.listdir(directory_path):
        
        # Check if the file is a file
        if os.path.isfile(os.path.join(directory_path, file)):
            
            # Check if the file is an image
            if file.endswith('.jpg') or file.endswith('.jpeg'):
                
                # Read the image
                image = Image.open(os.path.join(directory_path, file))
                
                # Append the image to the list
                images.append(image)
    return images

# write a function that conerts a string to json
def string_to_json(string):
    return json.loads(string.tolower())

# how can I get values from a dictionary


# Create a function to parse the JSON response
def parse_json_response(response, image):

    # Create an expression to convert all the keys in the response to lowercase
    #   
    # Parse the JSON response
    results = []
    json_response = response.json()

    json_response = json_response.lower()

    json_response = json.loads(json_response)  
    
    # Extract the name, model, retail price, and website from the JSON response
    # Use indexing to extract the values from the JSON response
    json_response = json.loads(json_response['choices'][0]['message']['content'])

    path_to_image = image.filename

    name = json_response['name']
    model = json_response['model']
    retail_price = json_response['price']
    website = json_response['website']
    print("Name: ", name)
    print("Model: ", model)
    print("Retail Price: ", retail_price)
    print("Website: ", website)
    columns = ["name", "model", "retail_price", "website"]
    results = name, model, retail_price, website
    # Add column to df_response

    df_response = pd.json_normalize(json_response)
    df_response['path_to_image'] = path_to_image
    df_response.to_csv(r'C:\Users\benji\OneDrive\Documents\Open AI_output.csv', index=False, mode='a', header=False)    

    
    return name, model, retail_price, website

# Create a function to append to a csv
def append_to_csv(results, output_file):
    # Create a pandas DataFrame from the results
    df = pd.DataFrame(results, columns=['Name', 'Model', 'Retail Price', 'Website'])
    
    # Append the DataFrame to a csv file
    df.to_csv(output_file, mode='a', index=False, header=False)

# Create a function to write the results to an excel file
def write_results_to_excel(results, output_file):
    # Create a pandas DataFrame from the results
    df = pd.DataFrame(results, columns=['Name', 'Model', 'Retail Price', 'Website'])
    
    # Write the DataFrame to an excel file
    df.to_excel(output_file, index=False)


# Create a function to append all teh responses to a csv file
def append_responses_to_csv(responses, output_file):
    # Create a list to store the results
    results = []
    
    # Loop through all the responses
    for response in responses:
        # Parse the JSON response
        name = parse_json_response(response)[0]
        model = parse_json_response(response)[1]
        retail_price = parse_json_response(response)[2]
        website = parse_json_response(response)[3]
        
        
        # Append the results to the list
        results.append([name, model, retail_price, website])
    
    # Write the results to an excel file
    write_results_to_excel(results, output_file)



dir_of_images = r'C:\Users\benji\Downloads\309 Hirsch\309 Hirsch'

list_images = read_images_from_directory(dir_of_images)

for image in list_images:
    resized_image = resize_image(image, 200, 200)
    b64_image_string = image_to_base64(resized_image)
    response = call_openai_api(b64_image_string)
    parse_json_response(response, image)
    # print(response)




