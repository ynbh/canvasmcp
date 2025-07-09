
import { tool } from "ai";
import { listEnabledFeaturesUsersDataSchema } from "./aitm.schema.ts";
import { listEnabledFeaturesUsers, ListEnabledFeaturesUsersData } from "..";

export default tool({
  description: `
  List enabled features
A paginated list of all features that are enabled on a given Account, Course,
or User.
Only the feature names are returned.
    `,
  parameters: listEnabledFeaturesUsersDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListEnabledFeaturesUsersData, "url"> ) => {
    try {
      const { data } = await listEnabledFeaturesUsers(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    