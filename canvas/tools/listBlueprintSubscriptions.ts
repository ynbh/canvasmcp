
import { tool } from "ai";
import { listBlueprintSubscriptionsDataSchema } from "./aitm.schema.ts";
import { listBlueprintSubscriptions, ListBlueprintSubscriptionsData } from "..";

export default tool({
  description: `
  List blueprint subscriptions
Returns a list of blueprint subscriptions for the given course.
(Currently a course may have no more than one.)
    `,
  parameters: listBlueprintSubscriptionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListBlueprintSubscriptionsData, "url"> ) => {
    try {
      const { data } = await listBlueprintSubscriptions(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    