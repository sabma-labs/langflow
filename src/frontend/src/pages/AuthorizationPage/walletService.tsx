import {
  Network,
  EntryFunctionABI,
  TypeTagAddress,
  TypeTagBool,
  TypeTagU128,
  AccountAddress,
  EndlessConfig,
  Endless,
  AccountAuthenticator,
  TypeTagU64,
  TypeTagU8,
  TypeTagVector,
  stringStructTag,
  TypeTagStruct,
  MoveString,
  MoveVector,
  U8
} from '@endlesslab/endless-ts-sdk';

import {
  EndlessLuffaSdk,
  UserResponseStatus,
  EndlessSignAndSubmitTransactionInput,
  EndlessWalletTransactionType,
} from '@luffalab/luffa-endless-sdk';

// Initialize the Luffa SDK for wallet interactions
const jssdk = new EndlessLuffaSdk({
  network: 'testnet', // or 'mainnet'
});

// Initialize the core Endless SDK for building transactions (optional if not used)
const endless = new Endless(new EndlessConfig({ network: Network.TESTNET }));

/**
 * Connects the user's wallet, constructs and signs a transaction, then disconnects.
 * @param data - Object containing method and parameters for the transaction
 * @returns Deserialized transaction authenticator on success
 * @throws Error if connection or signing is rejected
 */
export async function connectAndSubmit(data: Record<string, any>) {
  // 1. Prompt user to connect their wallet
  console.log('Connecting wallet...');
  const connectRes = await jssdk.connect();
  if (connectRes.status !== UserResponseStatus.APPROVED) {
    throw new Error('Wallet connection rejected by user');
  }
  console.log("Data being passed to getPayload:", JSON.stringify(data));
  // 2. Build the payload based on requested method
  const payloadData = getPayload(data);
  // const txn = await endless.transaction.build.simple({
  //   sender: sender,
  //   data: payloadData.payload
  // });
  try {
    console.log("FULL PAYLOAD JSON:", JSON.stringify(payloadData.payload));
  } catch (e) {
    console.error("❌ payloadData.payload is not JSON-serializable:", e);
    throw e;
  }
  try {
    const transactionRes = await jssdk.signAndSubmitTransaction(payloadData);
    if (transactionRes.status !== UserResponseStatus.APPROVED) {
      throw new Error("User rejected the transaction");
    }
  } catch (e) {
    alert("💥 signAndSubmitTransaction failed:");
    alert(e)
    throw e;
  } finally {
    await jssdk.disconnect();
  }

}

/**
 * Chooses the correct payload builder based on data.method
 */
function getPayload(data: Record<string, any>): EndlessSignAndSubmitTransactionInput {
  switch (data.function) {
    case 'create_nft_collection':
      return buildCreateCollectionPayload(data);
    case 'mint_nft':
      return buildMintNFTPayload(data)  
    default:
      throw new Error(`Unsupported method: ${data.function}`);
  }
}

/**
 * Builds payload for creating a new NFT collection
 */
function buildCreateCollectionPayload(data: Record<string, any>): EndlessSignAndSubmitTransactionInput {
  const abi: EntryFunctionABI = {
    typeParameters: [],
    parameters: [
      new TypeTagVector(new TypeTagU8()),
      new TypeTagU64(),
      new TypeTagVector(new TypeTagU8()),
      new TypeTagVector(new TypeTagU8()),
      new TypeTagBool(),
      new TypeTagBool(),
      new TypeTagBool(),
      new TypeTagBool(),
      new TypeTagBool(),
      new TypeTagBool(),
      new TypeTagBool(),
      new TypeTagBool(),
      new TypeTagBool(),
      new TypeTagU64(),
      new TypeTagU64(),
    ],
  };

  const args = [
    data.nft_collection_description,
    BigInt(100000),
    data.nft_collection_name,
    data.nft_collection_uri,
    true,
    true,
    true,
    true,
    true,
    true,
    true,
    true,
    true,
    BigInt(0),
    BigInt(990),
  ];

  return {
    payload: {
      function: '0x4::nft::create_collection',
      functionArguments: args,
      abi,
    },
  }  
};

  function buildMintNFTPayload(data: Record<string, any>): EndlessSignAndSubmitTransactionInput {
    const abi: EntryFunctionABI = {
      typeParameters: [],
      parameters: [
      new TypeTagStruct(stringStructTag()),
      new TypeTagStruct(stringStructTag()),
      new TypeTagStruct(stringStructTag()),
      new TypeTagStruct(stringStructTag()),
      // vector<string::String>
      new TypeTagVector(new TypeTagStruct(stringStructTag())),
      new TypeTagVector(new TypeTagStruct(stringStructTag())),
      // vector<vector<u8>>
      new TypeTagVector(TypeTagVector.u8()),
      ],
    };
    const strToBytes = (s: string) => Array.from(new TextEncoder().encode(s));
  
    const mv = MoveVector;
    const args = [
      // ← here’s the change: wrap each string with `strToBytes(...)`
      new MoveString(data.nft_collection_name),
      new MoveString(data.nft_description),
      new MoveString(data.nft_name),
      new MoveString(data.nft_uri),
      new MoveVector<MoveString>([]),  // empty vector<vector<u8>>
      new MoveVector<MoveString>([]),  // empty vector<vector<u8>>
      new MoveVector<MoveVector<U8>>([]),  // empty vector<vector<u8>>
    ];
    console.log("ARGS", args);
    return {
      payload: {
        function: '0x4::nft::mint_nft',
        functionArguments: args,
        abi,
      },
    };
  };
