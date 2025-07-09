
import { tool } from "ai";
import { reorderQuizItemsDataSchema } from "./aitm.schema.ts";
import { reorderQuizItems, ReorderQuizItemsData } from "..";

export default tool({
  description: `
  Reorder quiz items
Change order of the quiz questions or groups within the quiz

<b>204 No
Content</b> response code is returned if the reorder was successful.
    `,
  parameters: reorderQuizItemsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ReorderQuizItemsData, "url"> ) => {
    try {
      const { data } = await reorderQuizItems(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    