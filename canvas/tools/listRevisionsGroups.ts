
import { tool } from "ai";
import { listRevisionsGroupsDataSchema } from "./aitm.schema.ts";
import { listRevisionsGroups, ListRevisionsGroupsData } from "..";

export default tool({
  description: `
  List revisions
A paginated list of the revisions of a page. Callers must have update rights on the
page in order to see page history.
    `,
  parameters: listRevisionsGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListRevisionsGroupsData, "url"> ) => {
    try {
      const { data } = await listRevisionsGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    