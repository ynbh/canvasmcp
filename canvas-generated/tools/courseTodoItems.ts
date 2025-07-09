
import { tool } from "ai";
import { courseTodoItemsDataSchema } from "./aitm.schema.ts";
import { courseTodoItems, CourseTodoItemsData } from "..";

export default tool({
  description: `
  Course TODO items
Returns the current user's course-specific todo items.

For full documentation,
see the API documentation for the user todo items, in the user api.
    `,
  parameters: courseTodoItemsDataSchema.omit({ url: true }),
  execute: async (args : Omit<CourseTodoItemsData, "url"> ) => {
    try {
      const { data } = await courseTodoItems(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    