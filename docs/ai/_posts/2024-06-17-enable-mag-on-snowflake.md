# Enable MFA on Snowflake

## About Cloud Security

### An increase in security with minimal effort

This article defines the "how to" and some of the "why's" about enabling multi-factor authentication for your login to Snowflake.

### Why MFA?

I think about technology security as somethigng that is done im layers. Just like a security system at a home, you might have cameras in the driveway and on the doors to see who is there. That doesn't block anyone from entering so you would add dead bolts to your doors. In the house, you could
have a big friendly golden retriever to bark when someone arrives and to greet them with dog slobber upon entry. If one of these fails, you might still stay safe because the others hold up.

Likewise, with your Cloud accounts, no matter the provider, you have a few common, basic layers.

- User ID and password that you would know in your head which no one else knows.
- Role based authorization to make sure you can do and see exactly what you need - no more, no less. This way if the other two layers fail, the risk or "blast radius" is limited to what that one user can do.
- An authenticator tool such as Duo, Microsoft Authenticator or Google Authenticator (there are many.) The code provided is something you have that no one else has.

Snowdlake does in fact have all these, and uses the Duo authenticator. 

### One Way Cloud Breaches Happen 

When you hear about cloud data breaches, usually someone gets their hands on user ID's and passwords via spyware that steals passwords. It is exponentially harder for that person to get your "what you know" amd "what you have" because they are completely different systems. Never impossible but our security layers are about probabilities. So if they break through one layer, we want to make sure there are other layers, and that is what MFA is.

Access keys that aren't secured properly and insexure permissions (role based auth) are another couple pf common failures leading to breach. These are beyond the scope of this post but may become the topic of future posts. (Let me know your interest!)

## Setup MFA on your Snowflake Account

### Install Duo

Go to your phone's app store and look for Duo Mobile. Doenload and install. We will come baxk to the app later.

### 
