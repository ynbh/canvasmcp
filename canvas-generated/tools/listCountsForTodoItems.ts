
import { tool } from "ai";
import { listCountsForTodoItemsDataSchema } from "./aitm.schema.ts";
import { listCountsForTodoItems, ListCountsForTodoItemsData } from "..";

export default tool({
  description: `
  List counts for todo items
Counts of different todo items such as the number of assignments needing
grading as well as the number of assignments needing submitting.

There is a limit to the number of
todo items this endpoint will count.
It will only look at the first 100 todo items for the user. If
the user has more than 100 todo items this count may not be reliable.
The largest reliable number
for both counts is 100.
    `,
  parameters: listCountsForTodoItemsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListCountsForTodoItemsData, "url"> ) => {
    try {
      const { data } = await listCountsForTodoItems(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    