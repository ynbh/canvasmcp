
import { tool } from "ai";
import { updateWebhookSubscriptionDataSchema } from "./aitm.schema.ts";
import { updateWebhookSubscription, UpdateWebhookSubscriptionData } from "..";

export default tool({
  description: `
  Update a Webhook Subscription
This endpoint uses the same parameters as the create endpoint
    `,
  parameters: updateWebhookSubscriptionDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateWebhookSubscriptionData, "url"> ) => {
    try {
      const { data } = await updateWebhookSubscription(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    