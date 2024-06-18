# Enable MFA on Snowflake

## An increase in security with minimal effort

This article defines the "how to" and some of the "why's" about enabling multi-factor authentication for your login to Snowflake. Sridhar Ramawamy, CEO of Snowflake, posted on LinkedIn today (6/13/2024) about the importance of enabling MFA. I shared the link to his post below, but first, let's get your account secured.

## Setup MFA on your Snowflake Account

Directions as of June 17, 2024.

### Install Duo Mobile

Go to your phone's app store and search for Duo Mobile. Download and install. When it asks, make sure to give it permissions for using your camera and sending notifications. We will come back to the app later.

### Configure Your Account

I don't think you'll need screenshots; they make this pretty easy. But if it would be helpful, let me know as I am happy to add.

- On your Computer and on Snowflake's UI, Snowsight
  - Once logged into Snowflake on your computer (not phone), on the left navigation at the bottom you will see your user ID. Click the up caret next to your user name.
  - A menu will pop up. Click on "My Profile".
  - Scroll down and look for the "Multi-factor authentication" section. Click "Enroll".
  - Click on "start setup"
  - The next screen asks you what device you are using. Pick mobile phone.
  - Enter your phone number.
  - Pick if you are using an iPhone, Android, etc.
  - When it asks if you have Duo installed, since we did that before, click through on "I have Duo Mobile Installed"
  - A screen with a 2d barcode will be presented. At this time you are opening the Duo Mobile app on your phone.
- On your phone
  - If this is the first account you have with Duo Mobile, click "continue" to set up the first account.Then click "Use QR Code".
  - If you already have an account, click on "Add" in the top right corner and pick "Use QR Code".
  - Hold your phone up to scan the QR code on your computer screen.
- Conclusion
- Once scanned, your Snowflake account is now linked. 
- You can send a test push on the first connection. This allows you to see what the MFA experience is like; you will be prompted on your phone to approve the login.

That's all there is to making it harder for your account to be compromised.

### For administrators

There are multiple use cases for MFA such as CLI, JDBC connections and the legacy UI. Look in the Snowflake docs for handling these other combinations.

And in the not too distant future you will be seeing policies that you can apply to require users to use MFA.

## About Cloud Security

### Why MFA?

I think about technology security as something that is done im layers. Just like a security system at a home, you might have cameras in the driveway and on the doors to see who is there, along with an alarm that goes off when someone tries to get in. That doesn't block anyone from entering so you would add deadbolts to your doors. In the house, you could have a big friendly golden retriever to bark when someone arrives and to greet them with dog slobber upon entry. If one of these fails, you might still stay safe because the others hold up.

Likewise, with your Cloud accounts, no matter the provider, you have a few common, basic layers.

- User ID and password that you would know in your head which no one else knows.
- Role based authorization to make sure you can do and see exactly what you need - no more, no less. This way if the other two layers fail, the risk or "blast radius" is limited to what that one user can do.
- An authenticator tool such as Duo Mobile, Microsoft Authenticator or Google Authenticator (there are many.) The code provided is something you have that no one else has.

Snowdlake does in fact have all these layers.

### One Way Cloud Breaches Happen

When you hear about cloud data breaches, usually someone gets their hands on user IDs and passwords via spyware that steals passwords. It is exponentially harder for that person to get your "what you know" amd "what you have" because they are different systems. Unfortunately it is never impossible but our security layers are about probabilities. So if they break through one layer, we want to make sure there are other layers, and that is what MFA is.

Access keys that aren't secured properly and insexure permissions (role based auth) are another couple pf common failures leading to breach. These are beyond the scope of this post but may become the topic of future posts. (Let me know your interest!)

## References

- Snowflake's documentation about MFA: [https://docs.snowflake.com/en/user-guide/security-mfa](https://docs.snowflake.com/en/user-guide/security-mfa)
- Sridhar Ramaswamy's [post](https://www.linkedin.com/posts/sridhar-ramaswamy_since-our-founding-in-2012-the-security-activity-7208537215449141249-rGoW?utm_source=share&utm_medium=member_desktop)

