/**
 * conditional element management
 *
 * - conditional_field: str, id of the html element to be switched on or off
 * - switch_field: str, id of the form input that determins the on or off state
 * - switch_value: str, value of switch_field for which the conditional element should be switched on
 * - switch_show: bool, should visibility be switched on / off?
 * - switch_required: bool, should the `required` attribute be switched on / off?
 */
class ConditionalFieldSwitcher {
  constructor(conditional_field, switch_field, switch_value, switch_show = true, switch_required = true) {
    this.conditional_field_id = conditional_field;
    this.switch_field_id = switch_field;
    this.switch_value = switch_value;
    this.switch_show = switch_show;
    this.switch_required = switch_required;
    this.update();
  }
  /**
   * switch visibility and / or requiredness on
   */
  switch_on() {
    const conditional_field = document.getElementById(this.conditional_field_id);
    if(this.switch_show) {
      conditional_field.style.display = "";
    }
    if(this.switch_required) {
      conditional_field.required = true;
    }
  }
  /**
   * switch visibility and / or requiredness off
   */
  switch_off() {
    const conditional_field = document.getElementById(this.conditional_field_id);
    if(this.switch_show) {
      conditional_field.style.display = "none";
    }
    if(this.switch_required) {
      conditional_field.required = false;
    }
  }
  /**
   * switch on or off depending on the value of the switch field
   */
  update() {
    var switch_field = document.getElementById(this.switch_field_id);
    if (switch_field.value == this.switch_value) {
      this.switch_on();
    } else {
      this.switch_off();
    }
  }
}


/**
 * register a ConditionalFieldSwitcher as a change event handler for it's switch field.
 */
function register_switcher(switcher) {
  window.addEventListener("load", function () {
    document.getElementById(switcher.switch_field_id).addEventListener("change", function () {
      switcher.update();
    });
  });
}
