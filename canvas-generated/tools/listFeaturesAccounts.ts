
import { tool } from "ai";
import { listFeaturesAccountsDataSchema } from "./aitm.schema.ts";
import { listFeaturesAccounts, ListFeaturesAccountsData } from "..";

export default tool({
  description: `
  List features
A paginated list of all features that apply to a given Account, Course, or User.
    `,
  parameters: listFeaturesAccountsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListFeaturesAccountsData, "url"> ) => {
    try {
      const { data } = await listFeaturesAccounts(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    