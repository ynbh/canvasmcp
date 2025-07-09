
import { tool } from "ai";
import { listUncollatedSubmissionVersionsDataSchema } from "./aitm.schema.ts";
import { listUncollatedSubmissionVersions, ListUncollatedSubmissionVersionsData } from "..";

export default tool({
  description: `
  List uncollated submission versions
Gives a paginated, uncollated list of submission versions for
all matching
submissions in the context. This SubmissionVersion objects will not include
the
+new_grade+ or +previous_grade+ keys, only the +grade+; same for
+graded_at+ and +grader+.
    `,
  parameters: listUncollatedSubmissionVersionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListUncollatedSubmissionVersionsData, "url"> ) => {
    try {
      const { data } = await listUncollatedSubmissionVersions(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    