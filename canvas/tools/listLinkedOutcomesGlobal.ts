
import { tool } from "ai";
import { listLinkedOutcomesGlobalDataSchema } from "./aitm.schema.ts";
import { listLinkedOutcomesGlobal, ListLinkedOutcomesGlobalData } from "..";

export default tool({
  description: `
  List linked outcomes
A paginated list of the immediate OutcomeLink children of the outcome group.
    `,
  parameters: listLinkedOutcomesGlobalDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListLinkedOutcomesGlobalData, "url"> ) => {
    try {
      const { data } = await listLinkedOutcomesGlobal(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    