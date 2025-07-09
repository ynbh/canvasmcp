
import { tool } from "ai";
import { queryByUserDataSchema } from "./aitm.schema.ts";
import { queryByUser, QueryByUserData } from "..";

export default tool({
  description: `
  Query by user.
List authentication events for a given user.
    `,
  parameters: queryByUserDataSchema.omit({ url: true }),
  execute: async (args : Omit<QueryByUserData, "url"> ) => {
    try {
      const { data } = await queryByUser(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    