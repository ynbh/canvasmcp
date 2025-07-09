
import { tool } from "ai";
import { listEnabledFeaturesAccountsDataSchema } from "./aitm.schema.ts";
import { listEnabledFeaturesAccounts, ListEnabledFeaturesAccountsData } from "..";

export default tool({
  description: `
  List enabled features
A paginated list of all features that are enabled on a given Account, Course,
or User.
Only the feature names are returned.
    `,
  parameters: listEnabledFeaturesAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListEnabledFeaturesAccountsData, "url"> ) => {
    try {
      const { data } = await listEnabledFeaturesAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    