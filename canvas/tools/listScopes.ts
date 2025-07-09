
import { tool } from "ai";
import { listScopesDataSchema } from "./aitm.schema.ts";
import { listScopes, ListScopesData } from "..";

export default tool({
  description: `
  List scopes
A list of scopes that can be applied to developer keys and access tokens.
    `,
  parameters: listScopesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListScopesData, "url"> ) => {
    try {
      const { data } = await listScopes(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    