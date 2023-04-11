from flask import Flask, jsonify, request
from bs4 import BeautifulSoup
import requests
from flask import make_response


app = Flask(__name__)

# Login API


@app.route('/api/login', methods=['POST'])
def scrape_data():
    try:
        uname = request.form['uname']
        password = request.form['pass']
        payload = {
            "uname": uname,
            "pass": password
        }
        headers = {
            'User-agent':
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
        }
        el = requests.post(
            "http://juadmission.jdvu.ac.in/jums_exam/checklogindetails.do",
            headers=headers,
            data=payload)
        token = el.cookies['JSESSIONID']

        el.raise_for_status()  # Check for response errors

        soup = BeautifulSoup(el.text, "html.parser")
        image = soup.select("td")[9].select("img")[0].get("src")

        el = 'http://juadmission.jdvu.ac.in'+image  # image Link
        # print(el)

        exam_map = {}
        exam = soup.find_all('a', class_="easyui-linkbutton")
        # pop 1st element
        exam.pop(0)
        for i in exam:
            exam_name = i.find('b').text.strip()
            exam_url = i['href']
            exam_map[exam_name] = "http://juadmission.jdvu.ac.in"+exam_url

        allInfo = {
            "name": soup.select("td")[4].text.strip(),
            "department": soup.select("td")[8].text.strip(),
            "image": el,
            "exam": exam_map,
            "token": token
        }

        return jsonify(allInfo)

    except requests.exceptions.HTTPError as err:
        return jsonify({"error": "Something went wrong. Please try again."}), err.response.status_code

    except Exception as e:
        return jsonify({"error": "Something went wrong. Please try again."}), 500


# Forgot Password API
@app.route('/api/forgot', methods=['POST'])
def forgot_password():
    try:
        roll_no = request.form['roll_no']
        mobile_no = request.form['mobile_no']
        payload = {
            "roll_no": roll_no,
            "mobile_no": mobile_no
        }
        headers = {
            'User-agent':
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
        }
        el = requests.post(
            "http://juadmission.jdvu.ac.in/jums_exam/restpassword.do",
            headers=headers,
            data=payload)

        soup = BeautifulSoup(el.text, "html.parser")
        password = soup.select('b')[1].text.split(':')[1].split(' ')[1].strip()
        print(password)

        return jsonify({"password": password})

    except requests.exceptions.HTTPError as err:
        return jsonify({"error": "Something went wrong. Please try again."}), err.response.status_code

    except Exception as e:
        return jsonify({"error": "Something went wrong. Please try again."}), 500

# Download Admit Card API


@app.route('/api/admit', methods=['POST'])
def download_admit_card():
    try:
        token = request.form['token']
        exam_url = request.form['exam_url']
        headers = {
            'User-agent':
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
        }
        cookies = {
            'JSESSIONID': token
        }
        el = requests.get(exam_url, headers=headers, cookies=cookies)
        soup = BeautifulSoup(el.text, "html.parser")
        link = soup.select_one('a[target="admit_card_window"]')
        link = 'http://juadmission.jdvu.ac.in'+link['href']

        print(link)

        return jsonify({"admit_card": link})

    except requests.exceptions.HTTPError as err:
        return jsonify({"error": "Something went wrong. Please try again."}), err.response.status_code

    except Exception as e:
        return jsonify({"error": "Something went wrong. Please try again."}), 500


# @app.route('/api/result', methods=['POST'])
# def download_result_card():
#     try:
#         token = request.form['token']
#         exam_url = request.form['exam_url']
#         headers = {
#             'User-agent':
#             "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
#         }
#         cookies = {
#             'JSESSIONID': token
#         }
#         el = requests.get(exam_url, headers=headers, cookies=cookies)
#         soup = BeautifulSoup(el.text, "html.parser")
#         link = soup.select_one('a[target="result_window"]')

#         link = 'http://juadmission.jdvu.ac.in'+link['href']

#         print(link)

#         return jsonify({"result": link})

#     except requests.exceptions.HTTPError as err:
#         return jsonify({"error": "Something went wrong. Please try again."}), err.response.status_code

#     except Exception as e:
#         return jsonify({"error": "Something went wrong. Please try again."}), 500

# Download Result Card API
@app.route('/api/result', methods=['POST'])
def download_result_card():
    try:
        token = request.form['token']
        exam_url = request.form['exam_url']
        headers = {
            'User-agent':
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
        }
        cookies = {
            'JSESSIONID': token
        }
        el = requests.get(exam_url, headers=headers, cookies=cookies)
        soup = BeautifulSoup(el.text, "html.parser")
        link = soup.select_one('a[target="result_window"]')

        download_url = 'http://juadmission.jdvu.ac.in' + link['href']

        response = requests.get(download_url, headers=headers, cookies=cookies)

        # Set the content type as application/pdf
        response_headers = {'Content-Type': 'application/pdf'}

        # Set the content disposition as attachment
        filename = "result_card.pdf"
        response_headers['Content-Disposition'] = f'attachment; filename="{filename}"'

        # Create a Flask response with the PDF content and headers
        flask_response = make_response(response.content)
        flask_response.headers = response_headers

        return flask_response

    except requests.exceptions.HTTPError as err:
        return jsonify({"error": "Something went wrong. Please try again."}), err.response.status_code

    except Exception as e:
        return jsonify({"error": "Something went wrong. Please try again."}), 500


if __name__ == '__main__':
    app.run(debug=True)
