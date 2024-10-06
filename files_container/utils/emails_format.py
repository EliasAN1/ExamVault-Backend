def verification_email_html(link ,code):
  return f'''
        <!DOCTYPE html>
    <html lang="en">

    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>Verify your ExamVault</title>
      <style>
        .wrapper {{
          height: 70vh;
        }}

        .container {{
          background: rgb(40, 40, 40);
        }}

        h1 {{
          text-align: center;
          color: rgb(60, 157, 255);
        }}

        p {{
          color: white;
          font-size: 17px;
          padding: 20px;
        }}

        #recovery-link {{
          text-decoration: none;
          color: rgb(60, 157, 255);
          padding: 2px;
          transition: 0.2s;
        }}

        #code {{
          font-size: 20px;
          font-weight: bolder;
          color: rgb(60, 157, 255);
        }}

        #expire {{
          color: red;
          font-size: 20px;
          text-align: center;
        }}

        #cancel {{
          color: rgb(216, 0, 0);
          text-decoration: none;
          transition: 0.2s;
        }}

        #recovery-link:hover {{
          color: white;
        }}
      </style>
    </head>

    <body>
    <div class="wrapper">
    <div class="container">
      <h1>ExamVault</h1>
      <p>Hello, we are happy that this email reached you. <br><br>
        Please enter this code in the link provided below: <span id="code">{code}</span></p>
        <p> This is a link: <a href="http://localhost:4200/verification/{link}" id="recovery-link">Verification link</a> </p>

        <p id="expire">The code will expire after 10 minutes!</p>

    <p style="font-weight: bolder;">If it was not you who did this action please ignore
    </div>
    </div>

    </body>

    </html>
        '''

def restoration_email_html(link ,code):
  return f'''
        <!DOCTYPE html>
    <html lang="en">

    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>Reset password</title>
      <style>
        .wrapper {{
          height: 70vh;
        }}

        .container {{
          background: rgb(40, 40, 40);
        }}

        h1 {{
          text-align: center;
          color: rgb(60, 157, 255);
        }}

        p {{
          color: white;
          font-size: 17px;
          padding: 20px;
        }}

        #recovery-link {{
          text-decoration: none;
          color: rgb(60, 157, 255);
          padding: 2px;
          transition: 0.2s;
        }}

        #code {{
          font-size: 20px;
          font-weight: bolder;
          color: rgb(60, 157, 255);
        }}

        #expire {{
          color: red;
          font-size: 20px;
          text-align: center;
        }}

        #cancel {{
          color: rgb(216, 0, 0);
          text-decoration: none;
          transition: 0.2s;
        }}

        #recovery-link:hover {{
          color: white;
        }}
      </style>
    </head>

    <body>
    <div class="wrapper">
    <div class="container">
      <h1>ExamVault</h1>
      <p>Hello, we are happy that this email reached you. <br><br>
        Please enter this code in the link provided below: <span id="code">{code}</span></p>
        <p> This is a link: <a href="http://localhost:4200/forgot-creds/{link}" id="recovery-link">Restoration Link</a> </p>

        <p id="expire">The code will expire after 10 minutes!</p>

    <p style="font-weight: bolder;">If it was not you who did this action please contact us immediately
    </div>
    </div>

    </body>

    </html>
        '''
