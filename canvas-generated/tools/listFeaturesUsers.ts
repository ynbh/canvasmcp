
import { tool } from "ai";
import { listFeaturesUsersDataSchema } from "./aitm.schema.ts";
import { listFeaturesUsers, ListFeaturesUsersData } from "..";

export default tool({
  description: `
  List features
A paginated list of all features that apply to a given Account, Course, or User.
    `,
  parameters: listFeaturesUsersDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListFeaturesUsersData, "url"> ) => {
    try {
      const { data } = await listFeaturesUsers(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    