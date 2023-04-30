from dataclasses import dataclass, field
from typing import List


@dataclass
class Summary:
    successful_fixes: List[List[str]] = field(default_factory=list)
    failed_fixes: List[List[str]] = field(default_factory=list)
    fixes_without_effect: List[List[str]] = field(default_factory=list)

    def add_command(self, cmd: List[str], buildozer_result: int) -> None:
        if buildozer_result == 0:
            self.successful_fixes.append(cmd)
        elif buildozer_result == 2:
            self.failed_fixes.append(cmd)
        elif buildozer_result == 3:
            self.fixes_without_effect.append(cmd)
        else:
            raise Exception(
                f"Running buildozer command '{cmd}' failed with the unexpected return code: {buildozer_result}"
            )

    def print_summary(self) -> None:
        print(f"\nSuccessful fixes: {len(self.successful_fixes)}")

        if self.failed_fixes:
            print(
                """
WARNING Some buildozer commands failed!
Common causes for this can be:
- The workspace has changed since the DWYU report files have been generated and thus some targets no longer exist.
- The target which is supposed to be fixed is not written directly in a BUILD file, but created by a macro.

Failed commands:"""
            )
            print("\n".join(f"- {x}" for x in self.failed_fixes))

        if self.fixes_without_effect:
            print(
                """
WARNING Some buildozer commands did not create a change!
Common causes for this can be:
- You are executing the apply fixes script multiple times on the same report file.
- The script is trying to remove an aliased target. DWYU is only aware of the resolved target, which buildozer cannot
  connect to the alias name in the dependency list.

Commands without effect:"""
            )
            print("\n".join(f"- {x}" for x in self.fixes_without_effect))
