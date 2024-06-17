# Enable MFA on Snowflake

## An increase in security with minimal effort

This article defines the "how to" and slme of the "why's" about enabling milti-factor authentication for uour login to Snowflake.

## Why MFA?

I think about technology security as somethign that is done im layers. Just like security system at a home, you might have cameras in the driveway and on the doors to see who is there. That doesn't block anyone from entering so you would add dead bolts to your doors. In the house, you could
have a big friendly golden retriever to bark when someone arrives and to greet them with dog slobber upon entry. And the baseball bat in the closet is the final line of defense that we hope to never have to use.

Likewise, with your Cloud accounts, no matter the provider, you have a few common, basic layers.

- User ID and password that you would know in your head which no one else knows.
- Role based authorization to make sure you can do and see exactly what you need - no more, no less. This way if the other two layers fail, the risk or "blast radius" is limited to what that one user can do.
- An authenticator tool such as Duo, Microsoft Authenticator or Google Authenticator (there are many.) The code provided is something you have that no one else has.

## One Way Cloud Breaches Happen 

When you hear about cloud data breaches, usually someone gets their hands on passwords via spyware that steals passwords. It is exponentially harder for that person to get your "what you know" amd "what you have" because they are completely different systems. Never impossible but our security layers are about probabilities.

Access keys that aren't sexured properly and insexure permissions (role based auth) are another couple pf common failures leading to breach, but that is beyond the scope of this article.

