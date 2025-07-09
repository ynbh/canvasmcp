
import { tool } from "ai";
import { queryByLoginDataSchema } from "./aitm.schema.ts";
import { queryByLogin, QueryByLoginData } from "..";

export default tool({
  description: `
  Query by login.
List authentication events for a given login.
    `,
  parameters: queryByLoginDataSchema.omit({ url: true }),
  execute: async (args : Omit<QueryByLoginData, "url"> ) => {
    try {
      const { data } = await queryByLogin(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    