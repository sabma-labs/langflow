// token_transfer.ts
import { Endless, Account } from "@endlesslab/endless-ts-sdk";

const [,, privateKey, recipient, amount, tokenType] = process.argv;

if (!privateKey || !recipient || !amount || !tokenType) {
  console.error("Missing arguments");
  process.exit(1);
}

(async () => {
  try {
    const endless = new Endless();
    const sender = Account.fromPrivateKey(privateKey);

    const transaction = await endless.transaction.build.simple({
      sender: sender.accountAddress,
      data: {
        function: "0x1::coin::transfer",
        typeArguments: [`0x1::coin::Coin<${tokenType}>`],
        functionArguments: [recipient, Number(amount)],
      },
    });

    const pendingTransaction = await endless.signAndSubmitTransaction({
      signer: sender,
      transaction,
    });

    console.log(JSON.stringify({
      hash: pendingTransaction.hash,
      sender: sender.accountAddress.toString(),
      recipient,
      amount,
      token: tokenType
    }));
  } catch (error) {
    console.error(JSON.stringify({ error: error.message || error }));
    process.exit(1);
  }
})();
