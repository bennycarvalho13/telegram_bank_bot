a bot is a simple mock banking application bot. Upon typing `/start`, the user should get a prompt with three inline buttons:

- Check Balance
- Deposit
- Withdraw

## Check Balance

Posts a message showing the user's balance. The balance starts at 0.

It should also tell the user the time the last deposit or withdrawal was made, and for what amount.

## Deposit

A multi-step process.

The first prompt asks how much the user wants to deposit. They can reply by typing a number (e.g. 100). It must 
validate that it's an integer > 0 and let user type another number if it's not valid.

The second prompt asks them to confirm the deposit for the given amount. They can "Confirm" or "Cancel".

Once "Confirm" it adds that amount to their balance and stores a record of the transaction.

## Withdraw

Withdraw is the same as Deposit, except:

- The amount withdrawn must be smaller than their balance
- Once completed it removes from their balance instead of adding.
